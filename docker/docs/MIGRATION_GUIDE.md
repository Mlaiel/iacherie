# Migration Guide

## Docker Platform Migration Guide for Ainflue

**Author:** Fahed Mlaiel (mlaiel@live.de)  
**Version:** 3.0  
**Date:** September 2025

### Migration Overview

This guide covers migration strategies for the Ainflue Docker platform, including version upgrades, platform migrations, and infrastructure changes.

### Pre-Migration Assessment

#### 1. Current State Analysis
```bash
#!/bin/bash
# pre-migration-assessment.sh

echo "=== Docker Environment Assessment ==="

# Docker version
echo "Docker Version:"
docker version

# System resources
echo "System Resources:"
docker system df
free -h
df -h

# Running services
echo "Current Services:"
docker service ls
docker stack ls

# Network configuration
echo "Networks:"
docker network ls

# Volume usage
echo "Volumes:"
docker volume ls
docker system df -v

# Image inventory
echo "Images:"
docker images --format "table {{.Repository}}\t{{.Tag}}\t{{.Size}}\t{{.CreatedAt}}"

# Export current configuration
docker stack config ainflue > current-stack-config.yml
docker node ls --format "table {{.Hostname}}\t{{.Status}}\t{{.Availability}}\t{{.ManagerStatus}}"
```

#### 2. Dependency Mapping
```python
# dependency-analyzer.py
import docker
import yaml
import json

class DependencyAnalyzer:
    def __init__(self):
        self.client = docker.from_env()
        
    def analyze_service_dependencies(self):
        """Analyze service dependencies"""
        services = self.client.services.list()
        dependencies = {}
        
        for service in services:
            service_name = service.name
            dependencies[service_name] = {
                'depends_on': [],
                'networks': [],
                'volumes': [],
                'secrets': [],
                'configs': []
            }
            
            # Get service configuration
            spec = service.attrs['Spec']
            
            # Analyze networks
            if 'Networks' in spec['TaskTemplate']:
                for network in spec['TaskTemplate']['Networks']:
                    dependencies[service_name]['networks'].append(network['Target'])
            
            # Analyze volumes
            if 'Mounts' in spec['TaskTemplate']['ContainerSpec']:
                for mount in spec['TaskTemplate']['ContainerSpec']['Mounts']:
                    dependencies[service_name]['volumes'].append(mount['Source'])
            
            # Analyze secrets
            if 'Secrets' in spec['TaskTemplate']['ContainerSpec']:
                for secret in spec['TaskTemplate']['ContainerSpec']['Secrets']:
                    dependencies[service_name]['secrets'].append(secret['SecretName'])
        
        return dependencies
    
    def generate_migration_order(self, dependencies):
        """Generate optimal migration order"""
        # Topological sort to determine migration order
        order = []
        # Implementation would go here
        return order

analyzer = DependencyAnalyzer()
deps = analyzer.analyze_service_dependencies()
print(json.dumps(deps, indent=2))
```

### Docker Version Migration

#### 1. Docker Engine Upgrade
```bash
#!/bin/bash
# docker-upgrade.sh

CURRENT_VERSION=$(docker version --format '{{.Server.Version}}')
TARGET_VERSION="24.0.6"

echo "Upgrading Docker from $CURRENT_VERSION to $TARGET_VERSION"

# Backup current configuration
cp /etc/docker/daemon.json /etc/docker/daemon.json.backup
docker stack config ainflue > ainflue-stack-backup.yml

# Drain nodes one by one
NODES=$(docker node ls --format "{{.Hostname}}")
for node in $NODES; do
    echo "Draining node: $node"
    docker node update --availability drain $node
    
    # SSH to node and upgrade
    ssh $node "
        # Stop Docker
        sudo systemctl stop docker
        
        # Install new version
        curl -fsSL https://get.docker.com -o get-docker.sh
        sudo sh get-docker.sh --version $TARGET_VERSION
        
        # Start Docker
        sudo systemctl start docker
    "
    
    # Wait for node to rejoin
    sleep 30
    docker node update --availability active $node
    
    # Verify node health
    docker node inspect $node --format '{{.Status.State}}'
done

echo "Docker upgrade completed"
```

#### 2. Docker Compose V2 Migration
```bash
#!/bin/bash
# compose-v2-migration.sh

# Convert compose files to v2 format
for compose_file in docker-compose*.yml; do
    echo "Converting $compose_file to Compose V2 format"
    
    # Create backup
    cp $compose_file $compose_file.v1.backup
    
    # Update version
    sed -i 's/version: "3.8"/version: "3.9"/' $compose_file
    
    # Update syntax for newer features
    sed -i 's/external_links:/external_links: # Deprecated/' $compose_file
    
    # Validate syntax
    docker-compose -f $compose_file config > /dev/null
    if [ $? -eq 0 ]; then
        echo "✓ $compose_file converted successfully"
    else
        echo "✗ Error converting $compose_file"
        mv $compose_file.v1.backup $compose_file
    fi
done
```

### Platform Migration

#### 1. Docker Swarm to Kubernetes Migration
```yaml
# kubernetes-migration.yml
apiVersion: v1
kind: ConfigMap
metadata:
  name: swarm-to-k8s-mapping
data:
  migration-plan.yaml: |
    services:
      api:
        swarm:
          image: ainflue/api:latest
          replicas: 3
          ports: ["8000:8000"]
        kubernetes:
          deployment: ainflue-api
          service: ainflue-api-service
          replicas: 3
          
      database:
        swarm:
          image: postgres:15
          volumes: ["postgres-data:/var/lib/postgresql/data"]
        kubernetes:
          statefulset: postgres
          pvc: postgres-data
          service: postgres-service
```

```python
# swarm-to-k8s-converter.py
import yaml
import docker

class SwarmToK8sConverter:
    def __init__(self):
        self.client = docker.from_env()
        
    def convert_service_to_deployment(self, service_name):
        """Convert Docker Swarm service to Kubernetes Deployment"""
        service = self.client.services.get(service_name)
        spec = service.attrs['Spec']
        
        deployment = {
            'apiVersion': 'apps/v1',
            'kind': 'Deployment',
            'metadata': {
                'name': service_name,
                'labels': {'app': service_name}
            },
            'spec': {
                'replicas': spec['Mode']['Replicated']['Replicas'],
                'selector': {'matchLabels': {'app': service_name}},
                'template': {
                    'metadata': {'labels': {'app': service_name}},
                    'spec': {
                        'containers': [{
                            'name': service_name,
                            'image': spec['TaskTemplate']['ContainerSpec']['Image'],
                            'ports': self._convert_ports(spec),
                            'env': self._convert_env_vars(spec),
                            'resources': self._convert_resources(spec)
                        }]
                    }
                }
            }
        }
        
        return deployment
    
    def _convert_ports(self, spec):
        """Convert Docker ports to Kubernetes ports"""
        ports = []
        if 'Ports' in spec['EndpointSpec']:
            for port in spec['EndpointSpec']['Ports']:
                ports.append({
                    'containerPort': port['TargetPort'],
                    'protocol': port.get('Protocol', 'TCP').upper()
                })
        return ports
    
    def _convert_env_vars(self, spec):
        """Convert environment variables"""
        env_vars = []
        if 'Env' in spec['TaskTemplate']['ContainerSpec']:
            for env in spec['TaskTemplate']['ContainerSpec']['Env']:
                key, value = env.split('=', 1)
                env_vars.append({'name': key, 'value': value})
        return env_vars
    
    def _convert_resources(self, spec):
        """Convert resource limits"""
        resources = {}
        if 'Resources' in spec['TaskTemplate']:
            limits = spec['TaskTemplate']['Resources'].get('Limits', {})
            if limits:
                resources['limits'] = {}
                if 'MemoryBytes' in limits:
                    resources['limits']['memory'] = f"{limits['MemoryBytes'] // 1024 // 1024}Mi"
                if 'NanoCPUs' in limits:
                    resources['limits']['cpu'] = f"{limits['NanoCPUs'] / 1000000000}m"
        return resources
```

#### 2. Cloud Platform Migration
```bash
#!/bin/bash
# cloud-migration.sh

SOURCE_CLOUD="aws"
TARGET_CLOUD="azure"

echo "Migrating from $SOURCE_CLOUD to $TARGET_CLOUD"

# Export current state
docker stack config ainflue > ainflue-export.yml
docker config ls --format "{{.Name}}" > configs-list.txt
docker secret ls --format "{{.Name}}" > secrets-list.txt

# Create migration package
mkdir -p migration-package/{configs,secrets,volumes}

# Export configurations
while read config; do
    docker config inspect $config > migration-package/configs/$config.json
done < configs-list.txt

# Backup volumes
while read volume; do
    docker run --rm -v $volume:/data -v $(pwd)/migration-package/volumes:/backup alpine \
        tar czf /backup/$volume.tar.gz -C /data .
done < <(docker volume ls -q)

# Deploy to target cloud
case $TARGET_CLOUD in
    "azure")
        az acr login --name ainflueregistry
        # Push images to Azure Container Registry
        ;;
    "gcp")
        gcloud auth configure-docker
        # Push images to Google Container Registry
        ;;
esac

echo "Migration package created in migration-package/"
```

### Zero-Downtime Migration

#### 1. Blue-Green Migration Strategy
```yaml
# blue-green-migration.yml
version: '3.8'
services:
  # Current production (Blue)
  api-blue:
    image: ainflue/api:v1.0
    deploy:
      replicas: 3
      labels:
        - "traefik.enable=true"
        - "traefik.http.routers.api.rule=Host(`api.ainflue.com`)"
        - "traefik.http.services.api.loadbalancer.server.port=8000"
  
  # New version (Green) - initially disabled
  api-green:
    image: ainflue/api:v2.0
    deploy:
      replicas: 3
      labels:
        - "traefik.enable=false"  # Initially disabled
        - "traefik.http.routers.api-green.rule=Host(`api.ainflue.com`) && Headers(`X-Version`, `green`)"
        - "traefik.http.services.api-green.loadbalancer.server.port=8000"
  
  # Load balancer for traffic switching
  traefik:
    image: traefik:v2.10
    command:
      - "--api.dashboard=true"
      - "--providers.docker.swarmMode=true"
      - "--entrypoints.web.address=:80"
    ports:
      - "80:80"
      - "8080:8080"
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock:ro
```

```bash
#!/bin/bash
# blue-green-switch.sh

echo "Starting Blue-Green deployment switch"

# Deploy green version
docker service update --label-add traefik.enable=true ainflue_api-green

# Wait for health checks
sleep 30

# Verify green is healthy
if curl -f http://api.ainflue.com/health -H "X-Version: green"; then
    echo "Green version is healthy, switching traffic"
    
    # Switch traffic to green
    docker service update --label-rm traefik.http.routers.api.rule ainflue_api-blue
    docker service update --label-add traefik.http.routers.api.rule=Host\(\`api.ainflue.com\`\) ainflue_api-green
    
    # Wait and verify
    sleep 60
    
    # Scale down blue
    docker service scale ainflue_api-blue=0
    
    echo "Blue-Green switch completed successfully"
else
    echo "Green version health check failed, rolling back"
    docker service update --label-add traefik.enable=false ainflue_api-green
fi
```

### Database Migration

#### 1. PostgreSQL Migration with Minimal Downtime
```bash
#!/bin/bash
# postgres-migration.sh

OLD_DB="postgres-old"
NEW_DB="postgres-new"
APP_SERVICE="ainflue_api"

echo "Starting PostgreSQL migration"

# Step 1: Set up replication
docker exec $OLD_DB psql -U postgres -c "
    CREATE ROLE replication_user REPLICATION LOGIN ENCRYPTED PASSWORD 'replication_pass';
    SELECT pg_create_physical_replication_slot('migration_slot');
"

# Step 2: Start new database as replica
docker run -d --name $NEW_DB \
    -e POSTGRES_DB=ainflue \
    -e POSTGRES_USER=ainflue \
    -e POSTGRES_PASSWORD=password \
    postgres:15

# Set up replication
docker exec $NEW_DB pg_basebackup -h $OLD_DB -D /var/lib/postgresql/data -U replication_user -W

# Step 3: Monitor replication lag
while true; do
    LAG=$(docker exec $OLD_DB psql -U postgres -t -c "
        SELECT EXTRACT(EPOCH FROM (now() - pg_last_xact_replay_timestamp()))::int;
    ")
    
    echo "Replication lag: ${LAG}s"
    
    if [ "$LAG" -lt 5 ]; then
        echo "Replication lag acceptable, proceeding with switch"
        break
    fi
    
    sleep 10
done

# Step 4: Stop application writes
docker service update --replicas 0 $APP_SERVICE

# Step 5: Promote new database
docker exec $NEW_DB pg_promote

# Step 6: Update application configuration
docker service update \
    --env-add DATABASE_HOST=$NEW_DB \
    --replicas 3 \
    $APP_SERVICE

echo "Database migration completed"
```

### Configuration Migration

#### 1. Environment Variable Migration
```python
# config-migration.py
import yaml
import os
import docker

class ConfigMigration:
    def __init__(self):
        self.client = docker.from_env()
        
    def migrate_env_vars_to_configs(self):
        """Migrate environment variables to Docker configs"""
        
        services = self.client.services.list()
        
        for service in services:
            spec = service.attrs['Spec']
            container_spec = spec['TaskTemplate']['ContainerSpec']
            
            if 'Env' in container_spec:
                env_vars = {}
                for env in container_spec['Env']:
                    key, value = env.split('=', 1)
                    if key.startswith('CONFIG_'):
                        env_vars[key] = value
                
                if env_vars:
                    # Create config file
                    config_name = f"{service.name}-config"
                    config_content = yaml.dump(env_vars)
                    
                    # Create Docker config
                    config = self.client.configs.create(
                        name=config_name,
                        data=config_content
                    )
                    
                    # Update service to use config
                    service.update(
                        config_refs=[{
                            'config_id': config.id,
                            'config_name': config_name,
                            'filename': '/app/config.yml'
                        }]
                    )
                    
                    print(f"Migrated {service.name} environment variables to config")
```

### Rollback Procedures

#### 1. Automated Rollback
```bash
#!/bin/bash
# rollback.sh

STACK_NAME="ainflue"
BACKUP_CONFIG="ainflue-backup.yml"

echo "Starting rollback procedure"

# Check if backup exists
if [ ! -f "$BACKUP_CONFIG" ]; then
    echo "Error: No backup configuration found"
    exit 1
fi

# Store current state for potential re-rollback
docker stack config $STACK_NAME > ainflue-current.yml

# Perform rollback
echo "Rolling back to previous configuration"
docker stack deploy -c $BACKUP_CONFIG $STACK_NAME

# Wait for services to stabilize
sleep 60

# Verify rollback
FAILED_SERVICES=$(docker service ls --filter "desired-state=running" --format "{{.Name}}" | while read service; do
    RUNNING=$(docker service ps $service --filter "desired-state=running" --format "{{.CurrentState}}" | grep -c "Running")
    DESIRED=$(docker service inspect $service --format "{{.Spec.Mode.Replicated.Replicas}}")
    
    if [ "$RUNNING" != "$DESIRED" ]; then
        echo $service
    fi
done)

if [ -z "$FAILED_SERVICES" ]; then
    echo "Rollback completed successfully"
else
    echo "Rollback failed for services: $FAILED_SERVICES"
    exit 1
fi
```

### Migration Validation

#### 1. Post-Migration Testing
```python
# migration-validation.py
import asyncio
import aiohttp
import time

class MigrationValidator:
    def __init__(self):
        self.base_url = "https://api.ainflue.com"
        self.test_endpoints = [
            "/health",
            "/api/v1/status",
            "/api/v1/audio/process",
            "/api/v1/user/profile"
        ]
    
    async def validate_migration(self):
        """Validate migration success"""
        
        print("Starting migration validation...")
        
        # Test API endpoints
        async with aiohttp.ClientSession() as session:
            for endpoint in self.test_endpoints:
                url = f"{self.base_url}{endpoint}"
                start_time = time.time()
                
                try:
                    async with session.get(url, timeout=10) as response:
                        response_time = time.time() - start_time
                        
                        if response.status == 200:
                            print(f"✓ {endpoint}: OK ({response_time:.2f}s)")
                        else:
                            print(f"✗ {endpoint}: {response.status}")
                            
                except Exception as e:
                    print(f"✗ {endpoint}: Error - {e}")
        
        # Test database connectivity
        await self.test_database_connectivity()
        
        # Test file uploads
        await self.test_file_operations()
        
        print("Migration validation completed")
    
    async def test_database_connectivity(self):
        """Test database operations"""
        # Implementation for database tests
        pass
    
    async def test_file_operations(self):
        """Test file upload/download operations"""
        # Implementation for file operation tests
        pass

if __name__ == "__main__":
    validator = MigrationValidator()
    asyncio.run(validator.validate_migration())
```

### Migration Best Practices

1. **Plan Thoroughly**: Document all dependencies and migration steps
2. **Test Migration**: Test in staging environment first
3. **Backup Everything**: Create comprehensive backups before migration
4. **Gradual Approach**: Migrate services incrementally when possible
5. **Monitor Closely**: Monitor system health during and after migration
6. **Have Rollback Plan**: Always have a tested rollback procedure
7. **Validate Results**: Thoroughly test system functionality post-migration
8. **Document Changes**: Document all changes made during migration