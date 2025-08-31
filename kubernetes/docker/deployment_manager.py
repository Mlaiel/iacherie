"""🚀 Docker Deployment Manager - IA-Influencer-Agent Platform
===========================================================
Expert: Lead Dev IA + DevOps Engineer + Orchestration Specialist
Creator: Fahed Mlaiel <mlaiel@live.de>
===========================================================

⚠️  PROPRIÉTÉ INTELLECTUELLE - AVERTISSEMENT LÉGAL ⚠️
Tout vol, copie ou utilisation non autorisée de ce code source,
de ce concept ou de cette propriété intellectuelle sans
l'autorisation écrite explicite de Fahed Mlaiel est strictement
interdite et constituera une violation des lois sur le droit d'auteur.

Professional Docker deployment manager for orchestrating the complete
IA-Influencer platform with all microservices and infrastructure.
"""from typing import Dict, List, Optional, Any, Union
import logging
import asyncio
import subprocess
import json
from pathlib import Path
from dataclasses import dataclass, field
import yaml

from .api_gateway import APIGatewayDockerConfig
from .backend_services import BackendServicesDockerConfig
from .ai_engines import AIEnginesDockerConfig
from .fingerprinting_engine import FingerprintingEngineDockerConfig
from .content_protection import ContentProtectionDockerConfig
from .monetization_engine import MonetizationEngineDockerConfig
from .database_cluster import DatabaseClusterDockerConfig
from .monitoring_stack import MonitoringStackDockerConfig

logger = logging.getLogger(__name__)

@dataclass
class DockerDeploymentManager:
    """Enterprise Docker Deployment Manager for IA-Influencer Platform"""    
    # Deployment Configuration
    environment: str = "production"
    platform_version: str = "2.0.0"
    registry_url: str = "registry.ia-influencer.com"
    
    # Network Configuration
    network_name: str = "ia-influencer-network"
    network_subnet: str = "172.20.0.0/16"
    
    # Service Configurations
    api_gateway_config: APIGatewayDockerConfig = field(default_factory=APIGatewayDockerConfig)
    backend_services_config: BackendServicesDockerConfig = field(default_factory=BackendServicesDockerConfig)
    ai_engines_config: AIEnginesDockerConfig = field(default_factory=AIEnginesDockerConfig)
    fingerprinting_config: FingerprintingEngineDockerConfig = field(default_factory=FingerprintingEngineDockerConfig)
    content_protection_config: ContentProtectionDockerConfig = field(default_factory=ContentProtectionDockerConfig)
    monetization_config: MonetizationEngineDockerConfig = field(default_factory=MonetizationEngineDockerConfig)
    database_config: DatabaseClusterDockerConfig = field(default_factory=DatabaseClusterDockerConfig)
    monitoring_config: MonitoringStackDockerConfig = field(default_factory=MonitoringStackDockerConfig)
    
    # Deployment Options
    enable_ssl: bool = True
    enable_monitoring: bool = True
    enable_backups: bool = True
    enable_auto_scaling: bool = True
    
    # Resource Configuration
    total_cpu_limit: str = "32000m"
    total_memory_limit: str = "64Gi"
    
    def __post_init__(self):
        """Initialize deployment manager"""        self.deployment_order = [
            "network",
            "volumes", 
            "database-cluster",
            "redis-cluster",
            "elasticsearch-cluster",
            "monitoring-stack",
            "backend-services",
            "ai-engines",
            "fingerprinting-engine",
            "content-protection",
            "monetization-engine",
            "api-gateway"
        ]
    
    def generate_master_docker_compose(self) -> Dict[str, Any]:
        """Generate master docker-compose.yml for entire platform"""        
        # Combine all services
        all_services = {}
        
        # API Gateway
        all_services.update({
            "api-gateway": self.api_gateway_config.generate_docker_compose_service()
        })
        
        # Backend Services
        backend_services = BackendServicesDockerConfig()
        all_services.update({
            "backend-services": backend_services.generate_docker_compose_service(),
            "backend-services-worker": backend_services.generate_celery_worker_service(),
            "backend-services-scheduler": backend_services.generate_celery_beat_service(),
            "backend-services-flower": backend_services.generate_flower_monitoring_service()
        })
        
        # AI Engines
        all_services.update({
            "ai-engines": self.ai_engines_config.generate_docker_compose_service()
        })
        
        # Fingerprinting Engine
        all_services.update({
            "fingerprinting-engine": self.fingerprinting_config.generate_docker_compose_service()
        })
        
        # Content Protection
        protection_services = ContentProtectionDockerConfig()
        all_services.update({
            "content-protection": protection_services.generate_docker_compose_service(),
            "content-protection-crawler": protection_services.generate_crawler_worker_service()
        })
        
        # Monetization Engine
        monetization_services = MonetizationEngineDockerConfig()
        all_services.update({
            "monetization-engine": monetization_services.generate_docker_compose_service(),
            "monetization-payments": monetization_services.generate_payment_worker_service()
        })
        
        # Database Cluster
        all_services.update(self.database_config.generate_docker_compose_services())
        
        # Monitoring Stack
        if self.enable_monitoring:
            all_services.update(self.monitoring_config.generate_docker_compose_services())
        
        # Add infrastructure services
        all_services.update(self._generate_infrastructure_services())
        
        # Generate networks
        networks = {
            self.network_name: {
                "driver": "bridge",
                "ipam": {
                    "config": [{"subnet": self.network_subnet}]
                }
            }
        }
        
        # Generate volumes
        volumes = self._generate_volumes()
        
        return {
            "version": "3.8",
            "services": all_services,
            "networks": networks,
            "volumes": volumes
        }
    
    def _generate_infrastructure_services(self) -> Dict[str, Any]:
        """Generate infrastructure services (Redis, Elasticsearch, etc.)"""        return {
            # Redis Cluster
            "redis": {
                "image": "redis:7-alpine",
                "container_name": "ia-influencer-redis",
                "restart": "unless-stopped",
                "ports": ["6379:6379"],
                "command": [
                    "redis-server",
                    "--appendonly", "yes",
                    "--maxmemory", "4gb",
                    "--maxmemory-policy", "allkeys-lru",
                    "--save", "900", "1",
                    "--save", "300", "10",
                    "--save", "60", "10000"
                ],
                "volumes": [
                    "redis_data:/data",
                    "./config/redis:/usr/local/etc/redis:ro"
                ],
                "networks": [self.network_name],
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
                    "test": "redis-cli ping || exit 1",
                    "interval": "30s",
                    "timeout": "10s",
                    "retries": 3
                }
            },
            
            # Elasticsearch
            "elasticsearch": {
                "image": "docker.elastic.co/elasticsearch/elasticsearch:8.11.0",
                "container_name": "ia-influencer-elasticsearch",
                "restart": "unless-stopped",
                "ports": ["9200:9200", "9300:9300"],
                "environment": {
                    "discovery.type": "single-node",
                    "ES_JAVA_OPTS": "-Xms2g -Xmx2g",
                    "xpack.security.enabled": "false",
                    "xpack.security.enrollment.enabled": "false"
                },
                "volumes": [
                    "elasticsearch_data:/usr/share/elasticsearch/data",
                    "./config/elasticsearch:/usr/share/elasticsearch/config:ro"
                ],
                "networks": [self.network_name],
                "deploy": {
                    "resources": {
                        "limits": {
                            "cpus": "4000m",
                            "memory": "4Gi"
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
                }
            },
            
            # Qdrant Vector Database
            "qdrant": {
                "image": "qdrant/qdrant:v1.7.0",
                "container_name": "ia-influencer-qdrant",
                "restart": "unless-stopped",
                "ports": ["6333:6333", "6334:6334"],
                "volumes": [
                    "qdrant_data:/qdrant/storage",
                    "./config/qdrant:/qdrant/config:ro"
                ],
                "networks": [self.network_name],
                "deploy": {
                    "resources": {
                        "limits": {
                            "cpus": "2000m",
                            "memory": "4Gi"
                        }
                    }
                },
                "healthcheck": {
                    "test": "curl -f http://localhost:6333/health || exit 1",
                    "interval": "30s",
                    "timeout": "10s",
                    "retries": 3
                }
            },
            
            # Nginx Reverse Proxy
            "nginx": {
                "image": "nginx:alpine",
                "container_name": "ia-influencer-nginx",
                "restart": "unless-stopped",
                "ports": ["80:80", "443:443"],
                "volumes": [
                    "./config/nginx:/etc/nginx:ro",
                    "./ssl:/etc/ssl:ro",
                    "./logs/nginx:/var/log/nginx"
                ],
                "networks": [self.network_name],
                "depends_on": ["api-gateway"],
                "deploy": {
                    "resources": {
                        "limits": {
                            "cpus": "1000m",
                            "memory": "512Mi"
                        }
                    }
                },
                "healthcheck": {
                    "test": "curl -f http://localhost/health || exit 1",
                    "interval": "30s",
                    "timeout": "10s",
                    "retries": 3
                }
            }
        }
    
    def _generate_volumes(self) -> Dict[str, Any]:
        """Generate Docker volumes for all services"""        volumes = {
            # Database volumes
            "postgres_master_data": {},
            "postgres_replica_1_data": {},
            "postgres_replica_2_data": {},
            
            # Cache volumes
            "redis_data": {},
            
            # Search volumes
            "elasticsearch_data": {},
            "qdrant_data": {},
            
            # Monitoring volumes
            "prometheus_data": {},
            "grafana_data": {},
            "alertmanager_data": {},
            "loki_data": {},
            
            # Application volumes
            "celery_schedule": {},
            "model_cache": {},
            "content_uploads": {},
            "fingerprint_cache": {},
            "evidence_storage": {},
            "financial_reports": {}
        }
        
        return volumes
    
    def generate_deployment_scripts(self) -> Dict[str, str]:
        """Generate deployment scripts"""        
        scripts = {}
        
        # Build script
        scripts["build.sh"] = f"""#!/bin/bash
# IA-Influencer Platform Build Script
# Creator: Fahed Mlaiel <mlaiel@live.de>

set -e

echo "🚀 Building IA-Influencer Platform v{self.platform_version}"

# Build all service images
echo "📦 Building API Gateway..."
docker build -t {self.registry_url}/api-gateway:{self.platform_version} ./api-gateway/

echo "📦 Building Backend Services..."
docker build -t {self.registry_url}/backend-services:{self.platform_version} ./backend-services/

echo "📦 Building AI Engines..."
docker build -t {self.registry_url}/ai-engines:{self.platform_version} ./ai-engines/

echo "📦 Building Fingerprinting Engine..."
docker build -t {self.registry_url}/fingerprinting-engine:{self.platform_version} ./fingerprinting-engine/

echo "📦 Building Content Protection..."
docker build -t {self.registry_url}/content-protection:{self.platform_version} ./content-protection/

echo "📦 Building Monetization Engine..."
docker build -t {self.registry_url}/monetization-engine:{self.platform_version} ./monetization-engine/

echo "📦 Building Database Master..."
docker build -f ./database-cluster/Dockerfile.master -t {self.registry_url}/postgres-master:15.5 ./database-cluster/

echo "📦 Building Database Replica..."
docker build -f ./database-cluster/Dockerfile.replica -t {self.registry_url}/postgres-replica:15.5 ./database-cluster/

echo "✅ All images built successfully!"
"""        # Deploy script
        scripts["deploy.sh"] = f"""#!/bin/bash
# IA-Influencer Platform Deployment Script
# Creator: Fahed Mlaiel <mlaiel@live.de>

set -e

echo "🚀 Deploying IA-Influencer Platform v{self.platform_version}"

# Create necessary directories
mkdir -p logs/{{api-gateway,backend,ai-engines,fingerprinting,protection,monetization,postgres,nginx}}
mkdir -p config/{{api-gateway,backend,ai-engines,fingerprinting,protection,monetization,postgres,nginx,monitoring}}
mkdir -p ssl
mkdir -p backups
mkdir -p uploads
mkdir -p models
mkdir -p evidence
mkdir -p reports

# Set proper permissions
chmod -R 755 logs/
chmod -R 755 config/
chmod -R 700 ssl/
chmod -R 755 uploads/
chmod -R 755 models/

# Deploy infrastructure first
echo "🔧 Deploying infrastructure services..."
docker-compose -f docker-compose.infrastructure.yml up -d

# Wait for infrastructure to be ready
echo "⏳ Waiting for infrastructure services..."
sleep 30

# Deploy application services
echo "🚀 Deploying application services..."
docker-compose -f docker-compose.yml up -d

# Wait for services to be ready
echo "⏳ Waiting for application services..."
sleep 60

# Deploy monitoring stack
if [ "{str(self.enable_monitoring).lower()}" = "true" ]; then
    echo "📊 Deploying monitoring stack..."
    docker-compose -f docker-compose.monitoring.yml up -d
fi

echo "✅ Deployment completed successfully!"
echo "🌐 Platform available at: https://app.ia-influencer.com"
echo "📊 Monitoring available at: https://monitoring.ia-influencer.com"
"""        # Health check script
        scripts["health-check.sh"] = """#!/bin/bash
# IA-Influencer Platform Health Check Script
# Creator: Fahed Mlaiel <mlaiel@live.de>

echo "🏥 Checking IA-Influencer Platform Health..."

# Check core services
services=(
    "api-gateway:80"
    "backend-services:8000"
    "ai-engines:8000"
    "fingerprinting-engine:8000"
    "content-protection:8000"
    "monetization-engine:8000"
    "postgres-master:5432"
    "redis:6379"
    "elasticsearch:9200"
)

for service in "${services[@]}"; do
    name="${service%:*}"
    port="${service#*:}"
    
    if docker exec "$name" curl -f "http://localhost:$port/health" >/dev/null 2>&1; then
        echo "✅ $name: Healthy"
    else
        echo "❌ $name: Unhealthy"
    fi
done

echo "🏥 Health check completed!"
"""        # Backup script
        scripts["backup.sh"] = """#!/bin/bash
# IA-Influencer Platform Backup Script
# Creator: Fahed Mlaiel <mlaiel@live.de>

set -e

BACKUP_DIR="./backups/$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BACKUP_DIR"

echo "💾 Starting backup to $BACKUP_DIR..."

# Backup database
echo "📁 Backing up PostgreSQL database..."
docker exec postgres-master pg_dump -U ia_user ia_influencer | gzip > "$BACKUP_DIR/database.sql.gz"

# Backup volumes
echo "📁 Backing up Docker volumes..."
docker run --rm -v ia-influencer_postgres_master_data:/data -v "$PWD/$BACKUP_DIR":/backup alpine tar czf /backup/postgres_data.tar.gz -C /data .
docker run --rm -v ia-influencer_redis_data:/data -v "$PWD/$BACKUP_DIR":/backup alpine tar czf /backup/redis_data.tar.gz -C /data .
docker run --rm -v ia-influencer_elasticsearch_data:/data -v "$PWD/$BACKUP_DIR":/backup alpine tar czf /backup/elasticsearch_data.tar.gz -C /data .

# Backup configurations
echo "📁 Backing up configurations..."
tar czf "$BACKUP_DIR/config.tar.gz" config/
tar czf "$BACKUP_DIR/ssl.tar.gz" ssl/

echo "✅ Backup completed: $BACKUP_DIR"
"""        return scripts
    
    def save_deployment_configuration(self, output_dir: str) -> List[str]:
        """Save complete deployment configuration"""        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        files_created = []
        
        # Save master docker-compose.yml
        master_compose_path = output_path / "docker-compose.yml"
        with open(master_compose_path, 'w') as f:
            yaml.dump(self.generate_master_docker_compose(), f, default_flow_style=False, indent=2)
        files_created.append(str(master_compose_path))
        
        # Save deployment scripts
        scripts_dir = output_path / "scripts"
        scripts_dir.mkdir(exist_ok=True)
        
        for script_name, script_content in self.generate_deployment_scripts().items():
            script_path = scripts_dir / script_name
            with open(script_path, 'w') as f:
                f.write(script_content)
            script_path.chmod(0o755)  # Make executable
            files_created.append(str(script_path))
        
        # Save individual service configurations
        services_dir = output_path / "services"
        services_dir.mkdir(exist_ok=True)
        
        # Save each service configuration
        service_configs = [
            (self.api_gateway_config, "api-gateway"),
            (self.backend_services_config, "backend-services"),
            (self.ai_engines_config, "ai-engines"),
            (self.fingerprinting_config, "fingerprinting-engine"),
            (self.content_protection_config, "content-protection"),
            (self.monetization_config, "monetization-engine"),
            (self.database_config, "database-cluster"),
            (self.monitoring_config, "monitoring-stack")
        ]
        
        for config, service_name in service_configs:
            service_dir = services_dir / service_name
            service_files = config.save_config_files(str(service_dir))
            files_created.extend(service_files)
        
        # Generate environment files
        env_file_path = output_path / ".env"
        with open(env_file_path, 'w') as f:
            f.write(self._generate_env_file())
        files_created.append(str(env_file_path))
        
        # Generate README
        readme_path = output_path / "README.md"
        with open(readme_path, 'w') as f:
            f.write(self._generate_deployment_readme())
        files_created.append(str(readme_path))
        
        logger.info(f"✅ Complete deployment configuration saved: {len(files_created)} files created")
        return files_created
    
    def _generate_env_file(self) -> str:
        """Generate environment variables file"""        return f"""# IA-Influencer Platform Environment Configuration
# Creator: Fahed Mlaiel <mlaiel@live.de>
# Environment: {self.environment}

# Platform Configuration
PLATFORM_VERSION={self.platform_version}
ENVIRONMENT={self.environment}
REGISTRY_URL={self.registry_url}

# Network Configuration
NETWORK_NAME={self.network_name}
NETWORK_SUBNET={self.network_subnet}

# Database Configuration
POSTGRES_DB=ia_influencer
POSTGRES_USER=ia_user
POSTGRES_PASSWORD=ultra_secure_db_password_2024
POSTGRES_HOST=postgres-master
POSTGRES_PORT=5432

# Redis Configuration
REDIS_HOST=redis
REDIS_PORT=6379
REDIS_PASSWORD=

# Elasticsearch Configuration
ELASTICSEARCH_HOST=elasticsearch
ELASTICSEARCH_PORT=9200

# Security Configuration
JWT_SECRET_KEY=ultra_secure_jwt_secret_key_production_2024
ENCRYPTION_KEY=ultra_secure_encryption_key_32_chars_2024

# SSL Configuration
SSL_ENABLED={str(self.enable_ssl).lower()}
SSL_CERT_PATH=/etc/ssl/certs/ia-influencer.crt
SSL_KEY_PATH=/etc/ssl/private/ia-influencer.key

# Monitoring Configuration
MONITORING_ENABLED={str(self.enable_monitoring).lower()}
PROMETHEUS_URL=http://prometheus:9090
GRAFANA_URL=http://grafana:3000

# External API Keys (to be configured)
OPENAI_API_KEY=your_openai_api_key_here
ANTHROPIC_API_KEY=your_anthropic_api_key_here
HUGGINGFACE_API_KEY=your_huggingface_api_key_here

# Payment Gateway Keys (to be configured)
STRIPE_SECRET_KEY=your_stripe_secret_key_here
STRIPE_PUBLISHABLE_KEY=your_stripe_publishable_key_here
PAYPAL_CLIENT_ID=your_paypal_client_id_here
PAYPAL_CLIENT_SECRET=your_paypal_client_secret_here

# Social Media API Keys (to be configured)
YOUTUBE_API_KEY=your_youtube_api_key_here
INSTAGRAM_ACCESS_TOKEN=your_instagram_access_token_here
TIKTOK_API_KEY=your_tiktok_api_key_here
TWITTER_API_KEY=your_twitter_api_key_here

# Storage Configuration
S3_BUCKET=ia-influencer-storage
S3_REGION=eu-central-1
S3_ACCESS_KEY=your_s3_access_key_here
S3_SECRET_KEY=your_s3_secret_key_here

# Email Configuration
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your_email@ia-influencer.com
SMTP_PASSWORD=your_email_password_here
"""    def _generate_deployment_readme(self) -> str:
        """Generate deployment README"""        return f"""# 🚀 IA-Influencer Platform - Docker Deployment Guide

## Expert Team Specialties
- **Lead Dev IA + Backend Senior**: Architecture & Development
- **DevOps Engineer + Docker Specialist**: Infrastructure & Deployment  
- **ML Engineer + AI Processing**: Machine Learning & AI Models
- **Database Administrator + Performance Tuning**: Database Optimization
- **Security Engineer + Compliance Specialist**: Security & Protection
- **Microservices Architect + Scaling Expert**: System Architecture
- **Audio Engineer + Multi-format Processing**: Content Processing
- **IA Prompt Engineer + Content Analysis**: AI Content Analysis

## Creator & Copyright
**Creator**: Fahed Mlaiel <mlaiel@live.de>

⚠️ **AVERTISSEMENT LÉGAL** ⚠️  
Tout vol, copie ou utilisation non autorisée de ce code source, de ce concept ou de cette propriété intellectuelle sans l'autorisation écrite explicite de Fahed Mlaiel est strictement interdite et constituera une violation des lois sur le droit d'auteur.

## Platform Overview

IA-Influencer v{self.platform_version} is a comprehensive AI-powered platform for content protection and monetization, featuring:

- 🧠 **AI Engines**: Advanced content analysis and processing
- 🔍 **Fingerprinting Engine**: Multi-format content identification
- 🛡️ **Content Protection**: Real-time violation detection and monitoring
- 💰 **Monetization Engine**: Revenue tracking and automated payouts
- 📊 **Analytics Dashboard**: Comprehensive business intelligence
- 🔐 **Enterprise Security**: Multi-layer security and compliance

## Quick Start

### Prerequisites
- Docker Engine 20.10+
- Docker Compose 2.0+
- 32GB+ RAM recommended
- 500GB+ storage space
- SSL certificates for production

### Deployment Steps

1. **Clone Configuration**
   ```bash
   git clone https://github.com/ia-influencer/platform-deployment.git
   cd platform-deployment
   ```

2. **Configure Environment**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

3. **Build Platform**
   ```bash
   chmod +x scripts/*.sh
   ./scripts/build.sh
   ```

4. **Deploy Platform**
   ```bash
   ./scripts/deploy.sh
   ```

5. **Verify Deployment**
   ```bash
   ./scripts/health-check.sh
   ```

## Service Architecture

### Core Services
- **API Gateway** (Port 80/443): Main entry point and load balancer
- **Backend Services** (Port 8000): Core business logic and APIs
- **AI Engines** (Port 8000): Machine learning and AI processing
- **Fingerprinting Engine** (Port 8000): Content identification system
- **Content Protection** (Port 8000): Violation detection and monitoring
- **Monetization Engine** (Port 8000): Revenue and payment processing

### Infrastructure Services
- **PostgreSQL Cluster**: Primary database with read replicas
- **Redis**: Caching and session storage
- **Elasticsearch**: Search and analytics
- **Qdrant**: Vector database for similarity search

### Monitoring Stack
- **Prometheus**: Metrics collection
- **Grafana**: Visualization and dashboards
- **AlertManager**: Alert routing and management
- **Jaeger**: Distributed tracing
- **Loki**: Log aggregation

## Configuration

### Database Configuration
- Master-slave PostgreSQL cluster
- Automatic failover and replication
- Optimized for high-performance workloads

### Security Configuration
- SSL/TLS encryption for all communications
- JWT-based authentication
- Role-based access control
- API rate limiting and DDoS protection

### Scaling Configuration
- Horizontal pod autoscaling
- Load balancing across multiple instances
- Resource limits and requests optimization

## Monitoring & Alerting

### Key Metrics
- Service availability and response times
- Database performance and connections
- AI processing queue lengths
- Content violation detection rates
- Revenue tracking accuracy

### Alert Channels
- Email notifications
- Slack integration
- Webhook endpoints
- PagerDuty integration (optional)

## Backup & Recovery

### Automated Backups
- Daily database backups
- Configuration backups
- Volume snapshots
- 30-day retention policy

### Recovery Procedures
```bash
# Restore from backup
./scripts/restore.sh backup_date
```

## Troubleshooting

### Common Issues
1. **Service startup failures**: Check logs with `docker-compose logs [service]`
2. **Database connection issues**: Verify PostgreSQL cluster status
3. **High memory usage**: Monitor resource utilization with Grafana
4. **SSL certificate issues**: Check certificate validity and paths

### Support
For technical support, contact: mlaiel@live.de

## License & Copyright

This software is proprietary to Fahed Mlaiel. All rights reserved.
Unauthorized use, copying, or distribution is strictly prohibited.

© 2024 Fahed Mlaiel. All rights reserved.
"""    async def deploy_platform(self, output_dir: str) -> bool:
        """Deploy the entire IA-Influencer platform"""        try:
            logger.info("🚀 Starting IA-Influencer platform deployment...")
            
            # Save all configuration files
            files_created = self.save_deployment_configuration(output_dir)
            logger.info(f"📝 Configuration files created: {len(files_created)}")
            
            # Build all images
            logger.info("🔨 Building Docker images...")
            build_script = Path(output_dir) / "scripts" / "build.sh"
            if build_script.exists():
                result = subprocess.run([str(build_script)], capture_output=True, text=True)
                if result.returncode != 0:
                    logger.error(f"❌ Build failed: {result.stderr}")
                    return False
            
            # Deploy services
            logger.info("🚀 Deploying services...")
            deploy_script = Path(output_dir) / "scripts" / "deploy.sh" 
            if deploy_script.exists():
                result = subprocess.run([str(deploy_script)], capture_output=True, text=True)
                if result.returncode != 0:
                    logger.error(f"❌ Deployment failed: {result.stderr}")
                    return False
            
            logger.info("✅ IA-Influencer platform deployed successfully!")
            return True
            
        except Exception as e:
            logger.error(f"❌ Deployment failed: {e}")
            return False
