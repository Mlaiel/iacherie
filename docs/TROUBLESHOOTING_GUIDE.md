# 🔧 TROUBLESHOOTING GUIDE - DISTRIBUTION MODULE

**Version:** 3.0  
**Date:** Décembre 2024  
**Author:** Fahed Mlaiel (mlaiel@live.de)

---

## 🎯 OVERVIEW

Ce guide fournit des solutions aux problèmes courants rencontrés avec le module Distribution d'Ainflue, organisés par catégorie avec des solutions étape par étape.

## 🚨 PROBLÈMES CRITIQUES & SOLUTIONS

### ⚡ Performance Issues

#### 🐌 **Problème: Latence API > 50ms**

**Symptômes:**
- Temps de réponse API supérieur à 50ms
- Timeout des prédictions virales
- Lenteur distribution multi-plateformes

**Diagnostic:**
```bash
# Vérifier métriques performance
python -c "
import distribution.monitoring.performance_tracker as pt
tracker = pt.PerformanceTracker()
# Examiner les métriques temps réel
"

# Vérifier logs performance
tail -f logs/performance.log | grep "response_time"
```

**Solutions:**
1. **Optimisation Database:**
   ```python
   # Vérifier connexions DB
   from distribution.config.database_configs import DatabaseConfiguration
   config = DatabaseConfiguration()
   config.connection_pool_size = 20  # Augmenter pool
   config.query_timeout = 30  # Réduire timeout
   ```

2. **Cache Redis:**
   ```python
   # Activer cache pour prédictions virales
   from distribution.config.viral_configs import VIRAL_CONFIG
   VIRAL_CONFIG.cache_prediction_results = True
   VIRAL_CONFIG.cache_ttl_seconds = 1800  # 30 minutes
   ```

3. **Scaling Horizontal:**
   ```yaml
   # kubernetes/distribution-hpa.yaml
   spec:
     minReplicas: 20
     maxReplicas: 100
     targetCPUUtilizationPercentage: 60
   ```

#### 📊 **Problème: Consommation Mémoire Excessive**

**Symptômes:**
- RAM > 8GB par instance
- Memory leaks détectés
- OOM kills fréquents

**Diagnostic:**
```python
# Monitoring mémoire temps réel
import psutil
import gc

def diagnose_memory():
    process = psutil.Process()
    memory_info = process.memory_info()
    print(f"RSS: {memory_info.rss / 1024 / 1024:.2f} MB")
    print(f"VMS: {memory_info.vms / 1024 / 1024:.2f} MB")
    print(f"Garbage Objects: {len(gc.get_objects())}")
    
diagnose_memory()
```

**Solutions:**
1. **Optimisation Garbage Collection:**
   ```python
   import gc
   
   # Force garbage collection
   gc.collect()
   
   # Ajuster seuils GC
   gc.set_threshold(700, 10, 10)
   ```

2. **Limitation Buffer Size:**
   ```python
   # Dans performance_tracker.py
   self.metrics_buffer = defaultdict(lambda: deque(maxlen=500))  # Réduire de 1000
   self.request_times = deque(maxlen=500)  # Réduire buffer
   ```

### 🔒 Security Issues

#### 🚫 **Problème: Authentification Failed**

**Symptômes:**
- Erreurs 401/403 fréquentes
- JWT tokens invalides
- MFA failures

**Diagnostic:**
```python
# Vérifier configuration sécurité
from distribution.config.security_configs import SECURITY_CONFIG
issues = SECURITY_CONFIG.validate()
print("Issues trouvés:", issues)

# Vérifier JWT
import jwt
token = "your_jwt_token"
try:
    decoded = jwt.decode(token, SECURITY_CONFIG.authentication.jwt_secret_key, 
                        algorithms=[SECURITY_CONFIG.authentication.jwt_algorithm])
    print("JWT valide:", decoded)
except jwt.ExpiredSignatureError:
    print("JWT expiré")
except jwt.InvalidTokenError:
    print("JWT invalide")
```

**Solutions:**
1. **Régénération JWT Secret:**
   ```bash
   # Générer nouveau secret
   export JWT_SECRET_KEY=$(openssl rand -base64 64)
   ```

2. **Configuration MFA:**
   ```python
   from distribution.config.security_configs import SecurityConfig
   config = SecurityConfig()
   config.authentication.mfa_enabled = True
   config.authentication.mfa_methods = ["totp", "email"]
   ```

#### 🔍 **Problème: Audit Logs Manquants**

**Symptômes:**
- Logs audit vides
- Événements sécurité non enregistrés
- Compliance issues

**Diagnostic:**
```python
# Vérifier audit logger
from distribution.security.audit_logger import AuditLogger, AuditLogConfig
import os

config = AuditLogConfig()
print(f"Log path: {config.log_file_path}")
print(f"File exists: {os.path.exists(config.log_file_path)}")
print(f"Directory exists: {os.path.exists(os.path.dirname(config.log_file_path))}")
```

**Solutions:**
1. **Créer Répertoires Logs:**
   ```bash
   mkdir -p logs
   chmod 755 logs
   touch logs/audit.log
   chmod 644 logs/audit.log
   ```

2. **Initialisation Audit Logger:**
   ```python
   import asyncio
   from distribution.security.audit_logger import AuditLogger, AuditLogConfig
   
   async def setup_audit():
       config = AuditLogConfig()
       logger = AuditLogger(config)
       await logger.start()
       return logger
   
   audit_logger = asyncio.run(setup_audit())
   ```

### 🌐 Platform Connection Issues

#### 🔌 **Problème: Platform API Failures**

**Symptômes:**
- Erreurs 429 (Rate Limit)
- Connexions timeout
- Authentication failures plateformes

**Diagnostic:**
```python
# Test connexions plateformes
from distribution.platform_connectors_emerging import EmergingPlatformsManager
import asyncio

async def test_platforms():
    manager = EmergingPlatformsManager()
    
    # Test Mastodon
    from distribution.platform_connectors_emerging import MastodonConnector
    mastodon = MastodonConnector("https://mastodon.social", "test_token")
    result = await mastodon.connect()
    print(f"Mastodon: {result}")
    
asyncio.run(test_platforms())
```

**Solutions:**
1. **Rate Limiting Management:**
   ```python
   # Configuration rate limits
   from distribution.security.rate_limit_enforcer import RateLimitEnforcer
   
   rate_limiter = RateLimitEnforcer()
   
   # Ajouter règles par plateforme
   rate_limiter.add_rule("instagram", requests_per_hour=200)
   rate_limiter.add_rule("tiktok", requests_per_hour=300)
   ```

2. **Retry Logic avec Backoff:**
   ```python
   import asyncio
   import random
   
   async def retry_platform_call(func, max_retries=3):
       for attempt in range(max_retries):
           try:
               return await func()
           except Exception as e:
               if attempt == max_retries - 1:
                   raise
               wait_time = (2 ** attempt) + random.uniform(0, 1)
               await asyncio.sleep(wait_time)
   ```

#### 🌐 **Problème: Web3 Connection Failures**

**Symptômes:**
- RPC endpoints timeout
- Gas estimation failures
- Blockchain sync issues

**Diagnostic:**
```python
# Test Web3 connections
from distribution.platform_connectors_emerging import create_ethereum_connector

async def test_web3():
    connector = create_ethereum_connector(
        "https://eth.llamarpc.com",
        "your_private_key"
    )
    
    connected = await connector.connect()
    print(f"Ethereum connected: {connected}")
    
    if connected:
        balance = await connector.get_balance("0x742d35Cc6634C0532925a3b8D404d2Cc7c8b0532")
        print(f"Balance: {balance} ETH")

import asyncio
asyncio.run(test_web3())
```

**Solutions:**
1. **RPC Endpoint Backup:**
   ```python
   # Configuration multi-RPC
   ethereum_rpcs = [
       "https://eth.llamarpc.com",
       "https://rpc.ankr.com/eth",
       "https://ethereum.publicnode.com"
   ]
   
   async def connect_with_fallback(rpcs, private_key):
       for rpc in rpcs:
           try:
               connector = create_ethereum_connector(rpc, private_key)
               if await connector.connect():
                   return connector
           except Exception as e:
               print(f"RPC {rpc} failed: {e}")
               continue
       raise Exception("All RPC endpoints failed")
   ```

2. **Gas Optimization:**
   ```python
   # Configuration gas optimisée
   from distribution.platform_connectors_emerging import Web3Config
   
   config = Web3Config(
       network="ethereum",
       rpc_url="https://eth.llamarpc.com",
       private_key="your_key",
       gas_limit=150000,  # Augmenter limite
       gas_price_gwei=15  # Réduire prix si possible
   )
   ```

### 📊 Monitoring Issues

#### 📈 **Problème: Métriques Non Collectées**

**Symptômes:**
- Dashboards vides
- Alertes non déclenchées
- Performance data manquante

**Diagnostic:**
```python
# Vérifier collector métriques
from distribution.monitoring.performance_tracker import PerformanceTracker
import asyncio

async def test_metrics():
    tracker = PerformanceTracker()
    await tracker.start()
    
    # Test métrique
    await tracker.record_metric(
        "test.metric",
        100.0,
        MetricType.GAUGE
    )
    
    # Vérifier métriques
    summary = await tracker.get_metrics_summary(hours=1)
    print("Metrics collected:", len(summary))
    
    await tracker.stop()

asyncio.run(test_metrics())
```

**Solutions:**
1. **Redémarrage Monitoring:**
   ```python
   # Redémarrer services monitoring
   import asyncio
   from distribution.monitoring.performance_tracker import PerformanceTracker
   
   async def restart_monitoring():
       tracker = PerformanceTracker()
       await tracker.stop()  # Arrêter si running
       await asyncio.sleep(2)
       await tracker.start()  # Redémarrer
       print("Monitoring restarted")
   
   asyncio.run(restart_monitoring())
   ```

2. **Configuration Redis Monitoring:**
   ```python
   # Vérifier connexion Redis pour métriques
   redis_url = "redis://localhost:6379/0"
   tracker = PerformanceTracker(redis_url=redis_url)
   ```

## 🔍 DIAGNOSTIC TOOLS

### 🛠️ **Script Diagnostic Complet**

```python
#!/usr/bin/env python3
"""
Script de diagnostic complet pour Distribution Module
"""

import asyncio
import json
import psutil
import os
from datetime import datetime

async def run_full_diagnosis():
    print("🔍 DIAGNOSTIC DISTRIBUTION MODULE - AINFLUE")
    print("=" * 50)
    
    # 1. System Health
    print("\n📊 SYSTEM HEALTH:")
    cpu_percent = psutil.cpu_percent(interval=1)
    memory = psutil.virtual_memory()
    disk = psutil.disk_usage('/')
    
    print(f"  CPU Usage: {cpu_percent}%")
    print(f"  Memory Usage: {memory.percent}%")
    print(f"  Disk Usage: {(disk.used/disk.total)*100:.1f}%")
    
    # 2. Configuration Validation
    print("\n🔧 CONFIGURATION VALIDATION:")
    try:
        from distribution.config.viral_configs import VIRAL_CONFIG
        print(f"  ✅ Viral Config: {VIRAL_CONFIG.prediction.model_type.value}")
    except Exception as e:
        print(f"  ❌ Viral Config: {e}")
    
    try:
        from distribution.config.security_configs import SECURITY_CONFIG
        issues = SECURITY_CONFIG.validate()
        if not issues:
            print(f"  ✅ Security Config: {SECURITY_CONFIG.security_level.value}")
        else:
            print(f"  ⚠️  Security Issues: {len(issues)}")
    except Exception as e:
        print(f"  ❌ Security Config: {e}")
    
    # 3. Service Status
    print("\n🚀 SERVICE STATUS:")
    services = {
        "Performance Tracker": "distribution.monitoring.performance_tracker",
        "Audit Logger": "distribution.security.audit_logger",
        "Platform Connectors": "distribution.platform_connectors_emerging"
    }
    
    for service, module in services.items():
        try:
            __import__(module)
            print(f"  ✅ {service}: Available")
        except Exception as e:
            print(f"  ❌ {service}: {e}")
    
    # 4. File System Check
    print("\n📁 FILESYSTEM CHECK:")
    critical_paths = ["logs/", "distribution/config/", "distribution/security/"]
    
    for path in critical_paths:
        if os.path.exists(path):
            print(f"  ✅ {path}: Exists")
        else:
            print(f"  ❌ {path}: Missing")
            
    # 5. Dependencies Check
    print("\n📦 DEPENDENCIES CHECK:")
    required_packages = ["psutil", "aiofiles", "cryptography", "aiohttp"]
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"  ✅ {package}: Installed")
        except ImportError:
            print(f"  ❌ {package}: Missing")
    
    print(f"\n🕐 Diagnostic completed at: {datetime.now()}")

if __name__ == "__main__":
    asyncio.run(run_full_diagnosis())
```

### 📋 **Health Check Endpoint**

```python
# health_check.py
from fastapi import FastAPI, HTTPException
from datetime import datetime
import psutil

app = FastAPI()

@app.get("/health/distribution")
async def distribution_health_check():
    """Health check pour module distribution"""
    
    health_status = {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "components": {}
    }
    
    try:
        # Check system resources
        cpu_percent = psutil.cpu_percent()
        memory_percent = psutil.virtual_memory().percent
        
        health_status["components"]["system"] = {
            "status": "healthy" if cpu_percent < 80 and memory_percent < 80 else "degraded",
            "cpu_percent": cpu_percent,
            "memory_percent": memory_percent
        }
        
        # Check configuration
        try:
            from distribution.config.viral_configs import VIRAL_CONFIG
            health_status["components"]["viral_config"] = {
                "status": "healthy",
                "model_type": VIRAL_CONFIG.prediction.model_type.value
            }
        except Exception as e:
            health_status["components"]["viral_config"] = {
                "status": "unhealthy",
                "error": str(e)
            }
        
        # Check monitoring
        try:
            from distribution.monitoring.performance_tracker import PerformanceTracker
            health_status["components"]["monitoring"] = {"status": "healthy"}
        except Exception as e:
            health_status["components"]["monitoring"] = {
                "status": "unhealthy", 
                "error": str(e)
            }
        
        # Determine overall status
        component_statuses = [comp["status"] for comp in health_status["components"].values()]
        if "unhealthy" in component_statuses:
            health_status["status"] = "unhealthy"
        elif "degraded" in component_statuses:
            health_status["status"] = "degraded"
        
        return health_status
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Health check failed: {str(e)}")
```

## 📞 SUPPORT & ESCALATION

### 🆘 **Niveaux d'Escalation**

1. **Niveau 1 - Auto-résolution:**
   - Redémarrage services
   - Clear cache/logs
   - Configuration reset

2. **Niveau 2 - Investigation:**
   - Analyse logs détaillée
   - Profiling performance
   - Tests diagnostics

3. **Niveau 3 - Expert Support:**
   - Contact: mlaiel@live.de
   - Debug session
   - Architecture review

### 📊 **Collecte d'Informations Support**

```bash
# Script collecte logs pour support
#!/bin/bash
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
SUPPORT_DIR="support_data_${TIMESTAMP}"

mkdir -p ${SUPPORT_DIR}

# System info
echo "System Information:" > ${SUPPORT_DIR}/system_info.txt
uname -a >> ${SUPPORT_DIR}/system_info.txt
python --version >> ${SUPPORT_DIR}/system_info.txt
pip list >> ${SUPPORT_DIR}/system_info.txt

# Logs
cp logs/*.log ${SUPPORT_DIR}/ 2>/dev/null || echo "No logs found"

# Configuration
python -c "
from distribution.config.viral_configs import VIRAL_CONFIG
from distribution.config.security_configs import SECURITY_CONFIG
import json

with open('${SUPPORT_DIR}/config_summary.json', 'w') as f:
    config_data = {
        'viral_config': VIRAL_CONFIG.to_dict(),
        'security_level': SECURITY_CONFIG.security_level.value
    }
    json.dump(config_data, f, indent=2)
" 2>/dev/null || echo "Config export failed"

# Diagnostic
python test_new_modules.py > ${SUPPORT_DIR}/test_results.txt 2>&1

echo "Support data collected in: ${SUPPORT_DIR}"
tar -czf ${SUPPORT_DIR}.tar.gz ${SUPPORT_DIR}
echo "Archive created: ${SUPPORT_DIR}.tar.gz"
```

---

## 🎯 PRÉVENTION

### ✅ **Checklist Maintenance Préventive**

- [ ] **Hebdomadaire:** Vérifier logs audit et performance
- [ ] **Bi-hebdomadaire:** Rotation credentials et secrets
- [ ] **Mensuel:** Tests stress et monitoring capacité
- [ ] **Trimestriel:** Review configuration sécurité
- [ ] **Semestriel:** Audit complet et optimisation

### 📋 **Monitoring Proactif**

```python
# Configuration alertes préventives
from distribution.monitoring.performance_tracker import PerformanceThreshold

# Seuils performance
cpu_threshold = PerformanceThreshold(
    metric_name="system.cpu.percent",
    warning_threshold=70.0,
    critical_threshold=85.0,
    comparison="greater"
)

memory_threshold = PerformanceThreshold(
    metric_name="system.memory.percent", 
    warning_threshold=75.0,
    critical_threshold=90.0,
    comparison="greater"
)

response_time_threshold = PerformanceThreshold(
    metric_name="api.response_time.avg",
    warning_threshold=100.0,  # 100ms
    critical_threshold=200.0,  # 200ms
    comparison="greater"
)
```

---

**© 2024 Fahed Mlaiel - Troubleshooting Guide Distribution**  
**Contact: mlaiel@live.de | Support Enterprise 24/7**