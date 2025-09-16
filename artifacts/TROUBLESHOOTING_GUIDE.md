# 🔧 TROUBLESHOOTING GUIDE - AINFLUE ENTERPRISE

**Version:** 1.0 Enterprise  
**Date:** 15 Décembre 2025  
**Lead Architecture:** Fahed Mlaiel (mlaiel@live.de)  
**Équipe:** Lead Dev IA + Backend Senior + ML Engineer + DBA + Sécurité + Microservices + Audio + DevOps + IA Prompt Engineer

> **🚨 AVERTISSEMENT LÉGAL ULTRA-CRITIQUE** 🚨  
> **CE GUIDE DE DÉPANNAGE CONSTITUE LA PROPRIÉTÉ INTELLECTUELLE EXCLUSIVE DE FAHED MLAIEL**  
> **TOUTE UTILISATION SANS AUTORISATION ÉCRITE ENTRAÎNE POURSUITES LÉGALES**

---

## 🎯 GUIDE DE DÉPANNAGE ENTERPRISE

### 🚨 **INCIDENTS CRITIQUES - RÉPONSE IMMÉDIATE**

#### **Niveau 1: Système Down (RTO: 5 minutes)**
```bash
# 1. Vérification état général
kubectl get pods --all-namespaces | grep -v Running
docker ps --filter "status=exited"
systemctl status ainflue-*

# 2. Rollback immédiat si déploiement récent
kubectl rollout undo deployment/ainflue-api -n production
helm rollback ainflue-platform

# 3. Activation cluster de secours
kubectl config use-context disaster-recovery
terraform apply -var="activate_dr=true"
```

#### **Niveau 2: Performance Dégradée (RTO: 15 minutes)**
```bash
# 1. Analyse charge système
top -p $(pgrep -d',' python)
iostat -x 1 5
netstat -i

# 2. Vérification base de données
psql -c "SELECT * FROM pg_stat_activity WHERE state = 'active';"
redis-cli --latency-history

# 3. Scaling automatique d'urgence
kubectl scale deployment ainflue-api --replicas=10
docker service update --replicas 5 ainflue_worker
```

### 🔍 **DIAGNOSTICS PAR COMPOSANT**

#### **API Gateway Issues**
```bash
# Problème: 502/503 Errors
# Diagnostic:
curl -I https://api.ainflue.com/health
kubectl logs -f deployment/api-gateway -n production

# Solutions:
# 1. Redémarrage rolling
kubectl rollout restart deployment/api-gateway

# 2. Vérification upstream services
kubectl get endpoints -n production
kubectl describe service api-gateway

# 3. Configuration NGINX
nginx -t && systemctl reload nginx
```

#### **Base de Données PostgreSQL**
```sql
-- Problème: Requêtes lentes
-- Diagnostic:
SELECT query, mean_exec_time, calls 
FROM pg_stat_statements 
ORDER BY mean_exec_time DESC LIMIT 10;

-- Problème: Connections saturées
SELECT count(*), state FROM pg_stat_activity GROUP BY state;

-- Solutions:
-- 1. Kill requêtes longues
SELECT pg_terminate_backend(pid) 
FROM pg_stat_activity 
WHERE state = 'active' AND query_start < now() - interval '5 minutes';

-- 2. Optimisation index
REINDEX INDEX CONCURRENTLY idx_content_created_at;
ANALYZE;
```

#### **Redis Cache Issues**
```bash
# Problème: Memory exhaustion
redis-cli info memory

# Solutions:
# 1. Flush cache non-critique
redis-cli FLUSHDB 1  # Base 1 = cache temporaire

# 2. Optimisation mémoire
redis-cli CONFIG SET maxmemory-policy allkeys-lru
redis-cli CONFIG SET maxmemory 2gb

# 3. Monitoring clés
redis-cli --bigkeys
```

### 🤖 **IA AGENTS TROUBLESHOOTING (53 AGENTS)**

#### **Computer Vision Agents**
```python
# Problème: GPU Out of Memory
# Diagnostic:
nvidia-smi
docker stats $(docker ps -q --filter "label=ai-service")

# Solutions:
# 1. Réduction batch size
import torch
torch.cuda.empty_cache()

# 2. Optimisation modèles
# model.half()  # FP16 precision
# torch.backends.cudnn.benchmark = True

# 3. Distribution charge
kubectl scale deployment cv-processor --replicas=5
```

#### **NLP Processing Issues**
```python
# Problème: Transformer models timeout
# Diagnostic:
import psutil
print(f"Memory usage: {psutil.virtual_memory().percent}%")

# Solutions:
# 1. Model caching
from transformers import pipeline
nlp_pipeline = pipeline("sentiment-analysis", 
                       model="distilbert-base-uncased",
                       device=0,  # GPU
                       model_kwargs={"torch_dtype": torch.float16})

# 2. Async processing
import asyncio
async def process_text_batch(texts):
    results = await asyncio.gather(*[
        process_single_text(text) for text in texts
    ])
    return results
```

#### **Audio Processing Failures**
```python
# Problème: FFmpeg conversion errors
# Diagnostic:
ffprobe -v error -show_format input.mp3

# Solutions:
# 1. Format validation
import librosa
try:
    y, sr = librosa.load("audio.mp3", sr=22050)
except Exception as e:
    # Fallback conversion
    subprocess.run(["ffmpeg", "-i", "audio.mp3", "-ar", "22050", "output.wav"])

# 2. Streaming processing
def process_audio_stream(file_path):
    for chunk in librosa.stream(file_path, 
                               block_length=16, 
                               frame_length=2048, 
                               hop_length=512):
        yield process_chunk(chunk)
```

### 🌍 **PLATFORM INTEGRATIONS (65+ PLATEFORMES)**

#### **Instagram API Issues**
```python
# Problème: Rate limiting 429 errors
# Diagnostic:
headers = response.headers
rate_limit = {
    'limit': headers.get('X-RateLimit-Limit'),
    'remaining': headers.get('X-RateLimit-Remaining'),
    'reset': headers.get('X-RateLimit-Reset')
}

# Solutions:
# 1. Exponential backoff
import time
def retry_with_backoff(func, max_retries=3):
    for attempt in range(max_retries):
        try:
            return func()
        except RateLimitError:
            wait_time = 2 ** attempt
            time.sleep(wait_time)
    raise Exception("Max retries exceeded")

# 2. Request queuing
from celery import Celery
@celery.task(rate_limit='200/h')  # Instagram limit
def upload_to_instagram(content):
    return instagram_api.upload(content)
```

#### **YouTube Upload Failures**
```python
# Problème: Quota exceeded
# Solutions:
# 1. Multiple API keys rotation
class YouTubeAPIManager:
    def __init__(self):
        self.api_keys = ["key1", "key2", "key3"]
        self.current_key_index = 0
    
    def get_client(self):
        if self.quota_exceeded():
            self.rotate_key()
        return self.build_client(self.current_key())

# 2. Video chunked upload
def upload_large_video(video_path):
    resumable_upload = MediaFileUpload(
        video_path, 
        chunksize=1024*1024,  # 1MB chunks
        resumable=True
    )
    
    response = None
    while response is None:
        status, response = request.next_chunk()
        if status:
            print(f"Upload progress: {status.progress() * 100}%")
```

#### **Spotify Integration Issues**
```python
# Problème: Token expiration
# Solutions:
class SpotifyTokenManager:
    def __init__(self):
        self.token = None
        self.refresh_token = None
        self.expires_at = None
    
    def get_valid_token(self):
        if self.token_expired():
            self.refresh_access_token()
        return self.token
    
    def refresh_access_token(self):
        response = requests.post('https://accounts.spotify.com/api/token', {
            'grant_type': 'refresh_token',
            'refresh_token': self.refresh_token,
            'client_id': CLIENT_ID,
            'client_secret': CLIENT_SECRET
        })
        data = response.json()
        self.token = data['access_token']
        self.expires_at = time.time() + data['expires_in']
```

### 🔒 **SECURITY INCIDENTS**

#### **Détection d'Intrusion**
```bash
# 1. Analyse logs suspects
grep "FAILED LOGIN" /var/log/auth.log | tail -50
fail2ban-client status sshd

# 2. Vérification processus suspects
ps aux | grep -E "(bitcoin|crypto|mine)" 
netstat -tlnp | grep LISTEN

# 3. Isolation immédiate
iptables -A INPUT -s SUSPICIOUS_IP -j DROP
kubectl delete pod suspicious-pod --force --grace-period=0
```

#### **Fuite de Données Suspectée**
```bash
# 1. Audit accès fichiers
ausearch -f /sensitive/data -ts recent
lsof | grep deleted

# 2. Révocation tokens
redis-cli FLUSHALL  # Clear all sessions
kubectl create job revoke-tokens --from=cronjob/security-cleanup

# 3. Notification équipe sécurité
curl -X POST https://alerts.ainflue.com/security \
  -H "Content-Type: application/json" \
  -d '{"level":"critical","type":"data_breach_suspected"}'
```

### 💾 **STORAGE & BACKUP ISSUES**

#### **Espace Disque Saturé**
```bash
# 1. Diagnostic rapide
df -h
du -sh /* | sort -rh | head -10

# 2. Nettoyage d'urgence
docker system prune -af
journalctl --vacuum-time=7d
find /tmp -type f -atime +7 -delete

# 3. Extension automatique
# AWS EBS
aws ec2 modify-volume --volume-id vol-xxx --size 200
resize2fs /dev/xvdf

# Kubernetes PVC expansion
kubectl patch pvc data-pvc -p '{"spec":{"resources":{"requests":{"storage":"200Gi"}}}}'
```

#### **Backup Corruption**
```bash
# 1. Vérification intégrité
pg_verifybackup /backup/path
tar -tzf backup.tar.gz > /dev/null

# 2. Restoration alternative
# Point-in-time recovery
pg_restore --clean --if-exists --no-owner --dbname=ainflue /backup/latest.dump

# 3. Sync depuis replica
pg_basebackup -h replica.ainflue.com -D /var/lib/postgresql/data -U replication -W
```

### 🐳 **KUBERNETES TROUBLESHOOTING**

#### **Pods en CrashLoopBackOff**
```bash
# 1. Diagnostic détaillé
kubectl describe pod PODNAME
kubectl logs PODNAME --previous

# 2. Debug container
kubectl debug PODNAME -it --image=busybox

# 3. Resource constraints
kubectl top pods
kubectl describe node NODENAME
```

#### **Service Discovery Issues**
```bash
# 1. Vérification DNS
kubectl run test-pod --image=busybox --rm -it -- nslookup api-service

# 2. Endpoints validation
kubectl get endpoints api-service
kubectl describe service api-service

# 3. Network policies
kubectl describe networkpolicy
kubectl get pods --show-labels
```

### 📊 **MONITORING & ALERTING**

#### **Prometheus Issues**
```bash
# 1. Métriques manquantes
curl http://prometheus:9090/api/v1/label/__name__/values
curl http://localhost:9090/-/healthy

# 2. High cardinality
promtool query instant 'topk(10, count by (__name__)({__name__=~".+"}))'

# 3. Storage issues
df -h /prometheus
prometheus --storage.tsdb.retention.time=30d
```

#### **Grafana Dashboard Failures**
```bash
# 1. Datasource connectivity
curl -H "Authorization: Bearer $API_KEY" \
  http://grafana:3000/api/datasources/proxy/1/api/v1/label/__name__/values

# 2. Query optimization
# Réduire time range
# Utiliser recording rules
# Augmenter step interval
```

## 🚀 **PROCÉDURES D'ESCALADE**

### 📞 **Contacts d'Urgence**

#### **Niveau 1 Support (Réponse: 15 minutes)**
- **DevOps Engineer:** devops@ainflue.enterprise
- **Backend Engineer:** backend@ainflue.enterprise
- **Security Engineer:** security@ainflue.enterprise

#### **Niveau 2 Escalade (Réponse: 5 minutes)**
- **Lead Architect:** Fahed Mlaiel (mlaiel@live.de)
- **Emergency Hotline:** +33 1 XX XX XX XX
- **Slack:** #incident-response

#### **Niveau 3 Crisis (Réponse: Immédiate)**
- **CEO Notification:** Automatic if >30min downtime
- **Customer Communication:** Auto-generated status page
- **Media Response:** PR team activation

### 📋 **Incident Response Checklist**

```markdown
## Incident Response Template

### 1. IMMEDIATE (First 5 minutes)
- [ ] Acknowledge incident in monitoring system
- [ ] Create incident room: /invite-incident-team
- [ ] Initial impact assessment
- [ ] Customer notification if public-facing

### 2. INVESTIGATION (5-15 minutes)
- [ ] Collect system metrics and logs
- [ ] Identify root cause hypothesis
- [ ] Document timeline in incident doc
- [ ] Implement immediate mitigation

### 3. RESOLUTION (15-60 minutes)
- [ ] Apply permanent fix
- [ ] Validate system stability
- [ ] Monitor for regression
- [ ] Update status page

### 4. POST-MORTEM (24-48 hours)
- [ ] Root cause analysis
- [ ] Action items identification
- [ ] Process improvements
- [ ] Documentation updates
```

## 🔧 **AUTOMATION TOOLS**

### 🤖 **Self-Healing Scripts**

#### **Auto-restart Failed Services**
```bash
#!/bin/bash
# auto-heal.sh - Self-healing automation

check_service_health() {
    local service=$1
    if ! systemctl is-active --quiet $service; then
        echo "Service $service is down, restarting..."
        systemctl restart $service
        sleep 30
        
        if systemctl is-active --quiet $service; then
            echo "Service $service successfully restarted"
            notify_team "AUTO-HEAL: $service restarted successfully"
        else
            echo "CRITICAL: Failed to restart $service"
            escalate_incident "$service failed to restart"
        fi
    fi
}

# Monitor critical services
for service in ainflue-api ainflue-worker postgresql redis; do
    check_service_health $service
done
```

#### **Database Connection Pool Monitor**
```python
#!/usr/bin/env python3
# db-monitor.py - Auto-heal database connections

import psycopg2
import time
import subprocess
from prometheus_client import Counter, Gauge

connection_errors = Counter('db_connection_errors_total')
active_connections = Gauge('db_active_connections')

def check_db_health():
    try:
        conn = psycopg2.connect(
            host="localhost",
            database="ainflue",
            user="postgres",
            connect_timeout=5
        )
        
        cursor = conn.cursor()
        cursor.execute("SELECT count(*) FROM pg_stat_activity")
        count = cursor.fetchone()[0]
        active_connections.set(count)
        
        if count > 90:  # 90% of max connections
            kill_idle_connections()
            
        conn.close()
        return True
        
    except Exception as e:
        connection_errors.inc()
        restart_db_if_needed()
        return False

def kill_idle_connections():
    subprocess.run([
        "psql", "-c", 
        "SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE state = 'idle' AND query_start < now() - interval '30 minutes';"
    ])

if __name__ == "__main__":
    while True:
        check_db_health()
        time.sleep(60)
```

---

## 🚨 AVERTISSEMENTS LÉGAUX

### ⚖️ **PROPRIÉTÉ INTELLECTUELLE**

> **ATTENTION JURIDIQUE MAXIMALE:** Ce guide de dépannage et toutes les procédures, incluant mais non limitées aux scripts d'auto-réparation, les procédures d'incident response, les diagnostics avancés, et toutes les méthodologies de résolution contenues dans ce document sont la **propriété intellectuelle exclusive de Fahed Mlaiel**.

### 🛡️ **CLAUSES DE PROTECTION RENFORCÉES**
- ✅ **Copyright exclusif** Fahed Mlaiel 2025
- ✅ **Méthodologies propriétaires** protection légale
- ✅ **Scripts automatisés** propriété intellectuelle
- ✅ **Procédures d'escalade** confidentielles

### 📞 **SUPPORT TECHNIQUE D'URGENCE**

**Incident Response:** incident@ainflue.enterprise  
**Architecture Lead:** Fahed Mlaiel (mlaiel@live.de)  
**Emergency Hotline:** +33 1 XX XX XX XX

---

**© 2025 Fahed Mlaiel - Tous droits réservés**  
**Ainflue Platform Troubleshooting Guide**  
**Version 1.0 - Confidentiel et Propriétaire**