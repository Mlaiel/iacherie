# Disaster Recovery Plan

## Enterprise Disaster Recovery for Ainflue Platform

**Author:** Fahed Mlaiel (mlaiel@live.de)  
**Version:** 3.0  
**Date:** September 2025

### Overview

Comprehensive disaster recovery strategy ensuring 99.99% uptime and RTO < 4 hours for the Ainflue platform.

### Recovery Time Objectives (RTO) and Recovery Point Objectives (RPO)

| Service Tier | RTO | RPO | Priority |
|--------------|-----|-----|----------|
| Critical (API, Auth) | 15 minutes | 1 minute | P0 |
| Important (Processing) | 1 hour | 15 minutes | P1 |
| Standard (Analytics) | 4 hours | 1 hour | P2 |

### Multi-Region Architecture

#### 1. Primary Region Setup
```yaml
# Primary region (us-east-1)
version: '3.8'
services:
  api-gateway:
    deploy:
      replicas: 3
      placement:
        constraints:
          - node.labels.region==primary
  
  database:
    deploy:
      replicas: 1
      placement:
        constraints:
          - node.labels.role==database
```

#### 2. Disaster Recovery Region
```yaml
# DR region (us-west-2)
version: '3.8'
services:
  api-gateway-dr:
    deploy:
      replicas: 2
      placement:
        constraints:
          - node.labels.region==dr
```

### Automated Failover

#### 1. Health Check Based Failover
```python
# failover-controller.py
import asyncio
import aiohttp
from datetime import datetime, timedelta

class FailoverController:
    def __init__(self):
        self.primary_endpoint = "https://api.ainflue.com/health"
        self.dr_endpoint = "https://dr.api.ainflue.com/health"
        self.dns_controller = DNSController()
        
    async def monitor_health(self):
        consecutive_failures = 0
        
        while True:
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(self.primary_endpoint, timeout=10) as response:
                        if response.status == 200:
                            consecutive_failures = 0
                        else:
                            consecutive_failures += 1
                            
            except Exception:
                consecutive_failures += 1
            
            # Trigger failover after 3 consecutive failures
            if consecutive_failures >= 3:
                await self.initiate_failover()
                
            await asyncio.sleep(30)
    
    async def initiate_failover(self):
        print(f"Initiating failover at {datetime.now()}")
        
        # Update DNS to point to DR region
        await self.dns_controller.update_record(
            "api.ainflue.com", 
            self.dr_endpoint.replace("https://", "")
        )
        
        # Notify operations team
        await self.send_alert("Failover initiated to DR region")
```

### Database Recovery

#### 1. PostgreSQL Master-Slave Replication
```yaml
# postgresql-ha.yml
version: '3.8'
services:
  postgres-master:
    image: postgres:15
    environment:
      POSTGRES_REPLICATION_USER: replicator
      POSTGRES_REPLICATION_PASSWORD: ${REPLICATION_PASSWORD}
    command: |
      postgres 
      -c wal_level=replica 
      -c max_wal_senders=3 
      -c max_replication_slots=3
      
  postgres-slave:
    image: postgres:15
    environment:
      PGUSER: replicator
      PGPASSWORD: ${REPLICATION_PASSWORD}
    command: |
      bash -c "
      pg_basebackup -h postgres-master -D /var/lib/postgresql/data -U replicator -v -P -W
      echo 'standby_mode = on' >> /var/lib/postgresql/data/recovery.conf
      echo 'primary_conninfo = \"host=postgres-master port=5432 user=replicator\"' >> /var/lib/postgresql/data/recovery.conf
      postgres
      "
```

#### 2. Automated Database Failover
```bash
#!/bin/bash
# db-failover.sh

PRIMARY_DB="postgres-master"
STANDBY_DB="postgres-slave"

# Check primary database health
if ! docker exec $PRIMARY_DB pg_isready -U postgres; then
    echo "Primary database is down, promoting standby..."
    
    # Promote standby to primary
    docker exec $STANDBY_DB pg_ctl promote -D /var/lib/postgresql/data
    
    # Update application connection strings
    docker service update --env-add DATABASE_HOST=$STANDBY_DB ainflue_api
    
    # Send notification
    curl -X POST -H 'Content-type: application/json' \
        --data '{"text":"Database failover completed"}' \
        $SLACK_WEBHOOK_URL
fi
```

### Application Recovery

#### 1. Blue-Green Deployment for DR
```yaml
# blue-green-dr.yml
version: '3.8'
services:
  app-blue:
    image: ainflue/api:blue
    deploy:
      replicas: 0  # Standby
      
  app-green:
    image: ainflue/api:green
    deploy:
      replicas: 3  # Active
      
  load-balancer:
    image: nginx:alpine
    configs:
      - source: nginx-config
        target: /etc/nginx/nginx.conf
```

#### 2. Automated Application Recovery
```python
# app-recovery.py
import docker
import subprocess

class ApplicationRecovery:
    def __init__(self):
        self.docker_client = docker.from_env()
    
    def recover_failed_service(self, service_name):
        """Attempt to recover a failed service"""
        try:
            service = self.docker_client.services.get(service_name)
            
            # Get service tasks
            tasks = service.tasks()
            failed_tasks = [t for t in tasks if t['Status']['State'] == 'failed']
            
            if len(failed_tasks) > 2:  # More than 2 failed tasks
                print(f"Restarting service: {service_name}")
                service.force_update()
                
                # Scale up if needed
                current_replicas = service.attrs['Spec']['Mode']['Replicated']['Replicas']
                if current_replicas < 2:
                    service.update(mode={'Replicated': {'Replicas': 3}})
                    
        except Exception as e:
            print(f"Error recovering service {service_name}: {e}")
```

### Data Recovery Procedures

#### 1. Point-in-Time Recovery
```bash
#!/bin/bash
# point-in-time-recovery.sh

RECOVERY_TIME=$1  # Format: 2025-09-10 14:30:00
BACKUP_DIR="/backup/postgresql"

echo "Starting point-in-time recovery to: $RECOVERY_TIME"

# Stop current database
docker service scale ainflue_postgres=0

# Find appropriate base backup
BASE_BACKUP=$(find $BACKUP_DIR -name "backup_*.sql.gz" -newermt "$RECOVERY_TIME" | head -1)

if [ -z "$BASE_BACKUP" ]; then
    echo "No suitable base backup found"
    exit 1
fi

# Restore base backup
docker run --rm -v postgres-data:/var/lib/postgresql/data postgres:15 \
    bash -c "initdb -D /var/lib/postgresql/data && postgres &"

zcat $BASE_BACKUP | docker exec -i temp-postgres psql -U postgres

# Apply WAL files up to recovery time
# This would need access to WAL archives
apply_wal_to_time "$RECOVERY_TIME"

# Start database service
docker service scale ainflue_postgres=1
```

#### 2. Volume Recovery
```bash
#!/bin/bash
# volume-recovery.sh

VOLUME_NAME=$1
BACKUP_DATE=$2

echo "Recovering volume: $VOLUME_NAME from backup: $BACKUP_DATE"

# Stop services using the volume
SERVICES=$(docker service ls --filter label=com.docker.stack.namespace=ainflue -q)
for service in $SERVICES; do
    docker service scale $service=0
done

# Remove corrupted volume
docker volume rm $VOLUME_NAME

# Create new volume
docker volume create $VOLUME_NAME

# Restore from backup
docker run --rm \
    -v $VOLUME_NAME:/data \
    -v /backup/volumes/$VOLUME_NAME:/backup \
    alpine tar -xzf /backup/backup_$BACKUP_DATE.tar.gz -C /data

# Restart services
for service in $SERVICES; do
    docker service scale $service=1
done
```

### Infrastructure Recovery

#### 1. Docker Swarm Recovery
```bash
#!/bin/bash
# swarm-recovery.sh

echo "Recovering Docker Swarm cluster..."

# Re-initialize swarm if necessary
if ! docker info | grep -q "Swarm: active"; then
    docker swarm init --advertise-addr $(hostname -I | awk '{print $1}')
fi

# Restore node labels
docker node update --label-add region=primary $(docker node ls -q)
docker node update --label-add role=manager $(docker node ls -q --filter role=manager)

# Restore networks
docker network create --driver overlay --attachable ainflue-network
docker network create --driver overlay monitoring-network

# Restore secrets and configs
restore_secrets_and_configs

# Deploy services
docker stack deploy -c docker-compose.production.yml ainflue
```

#### 2. Configuration Recovery
```python
# config-recovery.py
import json
import subprocess

def restore_docker_configs():
    """Restore Docker configs from backup"""
    with open('/backup/configs/docker-configs-list.json', 'r') as f:
        configs = json.load(f)
    
    for config in configs:
        config_name = config['Spec']['Name']
        config_file = f"/backup/configs/{config_name}.json"
        
        try:
            # Remove existing config if it exists
            subprocess.run(['docker', 'config', 'rm', config_name], 
                         capture_output=True)
            
            # Create new config
            with open(config_file, 'r') as f:
                config_data = json.load(f)
                config_content = config_data['Spec']['Data']
                
            subprocess.run(['docker', 'config', 'create', config_name, '-'], 
                         input=config_content, text=True)
            
        except Exception as e:
            print(f"Error restoring config {config_name}: {e}")
```

### Recovery Testing

#### 1. Automated DR Testing
```python
# dr-test.py
import asyncio
import subprocess
from datetime import datetime

class DisasterRecoveryTest:
    def __init__(self):
        self.test_results = []
    
    async def run_full_dr_test(self):
        """Run comprehensive DR test"""
        print("Starting DR test...")
        
        # Test 1: Database failover
        await self.test_database_failover()
        
        # Test 2: Application failover
        await self.test_application_failover()
        
        # Test 3: Volume recovery
        await self.test_volume_recovery()
        
        # Test 4: Network connectivity
        await self.test_network_connectivity()
        
        # Generate report
        self.generate_test_report()
    
    async def test_database_failover(self):
        """Test database failover procedure"""
        start_time = datetime.now()
        
        try:
            # Simulate database failure
            subprocess.run(['docker', 'service', 'scale', 'ainflue_postgres=0'])
            
            # Wait for failover
            await asyncio.sleep(30)
            
            # Check if standby is promoted
            result = subprocess.run(['docker', 'exec', 'postgres-slave', 'pg_isready'], 
                                  capture_output=True)
            
            recovery_time = datetime.now() - start_time
            success = result.returncode == 0
            
            self.test_results.append({
                'test': 'Database Failover',
                'success': success,
                'recovery_time': recovery_time.total_seconds(),
                'rto_met': recovery_time.total_seconds() < 900  # 15 minutes
            })
            
        except Exception as e:
            self.test_results.append({
                'test': 'Database Failover',
                'success': False,
                'error': str(e)
            })
```

### Monitoring and Alerting

#### 1. DR Health Monitoring
```yaml
# dr-monitoring.yml
version: '3.8'
services:
  dr-monitor:
    image: prom/prometheus
    configs:
      - source: dr-prometheus-config
        target: /etc/prometheus/prometheus.yml
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
      - '--web.console.libraries=/etc/prometheus/console_libraries'

configs:
  dr-prometheus-config:
    content: |
      global:
        scrape_interval: 15s
      scrape_configs:
        - job_name: 'dr-endpoints'
          static_configs:
            - targets: ['dr.api.ainflue.com:443']
          metrics_path: /health
          scheme: https
```

### Communication Plan

#### 1. Incident Communication
```python
# incident-communication.py
class IncidentCommunication:
    def __init__(self):
        self.slack_webhook = os.environ['SLACK_WEBHOOK']
        self.email_service = EmailService()
        self.status_page = StatusPageAPI()
    
    async def notify_incident(self, severity, message):
        """Send incident notifications"""
        
        # Update status page
        await self.status_page.create_incident(severity, message)
        
        # Send Slack notification
        await self.send_slack_alert(severity, message)
        
        # Send email to on-call team
        if severity in ['critical', 'high']:
            await self.email_service.send_alert(
                recipients=['oncall@ainflue.com'],
                subject=f"[{severity.upper()}] Ainflue Incident",
                body=message
            )
    
    async def notify_recovery(self, incident_id):
        """Send recovery notifications"""
        await self.status_page.resolve_incident(incident_id)
        await self.send_slack_message("✅ System recovery completed")
```

### Recovery Runbooks

#### 1. Critical Service Recovery
```markdown
# Critical Service Recovery Runbook

## Scenario: API Service Down

### Immediate Actions (0-5 minutes)
1. Check service status: `docker service ps ainflue_api`
2. Check logs: `docker service logs ainflue_api`
3. Verify load balancer: `curl -I https://api.ainflue.com/health`

### Recovery Steps (5-15 minutes)
1. Scale service: `docker service scale ainflue_api=3`
2. Force update if needed: `docker service update --force ainflue_api`
3. Check database connectivity
4. Verify external dependencies

### Escalation (15+ minutes)
1. Activate DR region
2. Update DNS records
3. Notify executive team
```

### Best Practices

1. **Regular Testing**: Test DR procedures monthly
2. **Documentation**: Keep runbooks updated
3. **Automation**: Automate as much of the recovery as possible
4. **Monitoring**: Continuous monitoring of DR systems
5. **Training**: Regular DR training for operations team
6. **Communication**: Clear communication channels during incidents