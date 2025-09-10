# 🏗️ Infrastructure - Services Docker

**Infrastructure Docker de la Plateforme Ainflue**

Infrastructure Docker de niveau entreprise avec support multi-environnement, équilibrage de charge, découverte de services et orchestration automatique pour créateurs de contenu et influenceurs.

## 🎯 Services d'Infrastructure Principaux

### **Images Docker de Base**
- Builds multi-étapes optimisés pour charges de production
- Durcissement sécuritaire et surface d'attaque minimale
- Support multi-architecture (x86_64, ARM64)
- Mises à jour automatiques des dépendances et scan de vulnérabilités

### **Équilibreur de Charge et Reverse Proxy**
- Équilibrage de charge haute performance basé sur NGINX
- Terminaison SSL/TLS et gestion de certificats
- Limitation de taux et protection DDoS
- Vérifications de santé et basculement automatique

### **Découverte de Services**
- Enregistrement et découverte de services basés sur Consul
- Résolution de services basée sur DNS
- Intégration de vérifications de santé
- Communication de services multi-datacenter

### **Gestion de Configuration**
- Configuration centralisée avec Consul KV
- Configurations spécifiques à l'environnement
- Gestion des secrets et chiffrement au repos
- Mises à jour de configuration dynamiques sans arrêt

## 🛠️ Architecture d'Infrastructure

```yaml
# Services d'Infrastructure Docker Compose
version: '3.8'
services:
  nginx-lb:
    build: ./load-balancer.dockerfile
    environment:
      - UPSTREAM_SERVERS=${UPSTREAM_SERVERS}
      - SSL_CERT_PATH=${SSL_CERT_PATH}
      - RATE_LIMIT=${RATE_LIMIT:-100r/s}
    
  consul:
    build: ./service-discovery.dockerfile
    environment:
      - CONSUL_DATACENTER=${DATACENTER:-dc1}
      - CONSUL_ENCRYPT_KEY=${CONSUL_ENCRYPT_KEY}
      - CONSUL_ACL_TOKEN=${CONSUL_ACL_TOKEN}
```

## 🔧 Configuration Infrastructure

### Variables d'Environnement
```bash
# Équilibreur de Charge
UPSTREAM_SERVERS=app1:8000,app2:8000,app3:8000
SSL_CERT_PATH=/etc/ssl/certs
RATE_LIMIT=100r/s
MAX_CONNECTIONS=1000

# Découverte de Services
DATACENTER=dc1
CONSUL_ENCRYPT_KEY=base64_encrypted_key
CONSUL_ACL_TOKEN=secret_acl_token
SERVICE_TAGS=web,api,backend

# Gestion des Secrets
VAULT_ROOT_TOKEN=secret_root_token
VAULT_ADDR=http://vault:8200
SECRET_ENGINE=kv-v2
VAULT_NAMESPACE=ainflue
```

## 📊 Support Multi-Environnement

### Développement
- Hot-reload et débogage en direct
- Logging étendu et profilage
- Services simulés pour APIs externes
- Contrôles de sécurité réduits pour itération rapide

### Staging
- Configuration similaire à la production
- Exécution complète de la suite de tests
- Benchmarking de performance
- Scan de sécurité et vérifications de conformité

### Production
- Configuration haute disponibilité avec redondance
- Scaling automatique et équilibrage de charge
- Monitoring complet et alertes
- Déploiements sans temps d'arrêt avec mises à jour progressives

## 🚀 Démarrage

```bash
# Déployer l'infrastructure de base
docker-compose -f docker-compose.yml up -d

# Démarrer l'environnement de production
docker-compose -f docker-compose.production.yml up -d

# Vérifier la santé des services
docker-compose ps

# Statut de l'équilibreur de charge
curl http://localhost/health

# Tableau de bord de découverte de services
open http://localhost:8500
```

## 📈 Mise à l'Échelle et Performance

L'infrastructure supporte la mise à l'échelle automatique:
- **Autoscaling Horizontal de Pods** basé sur les métriques CPU/Mémoire
- **Autoscaling de Cluster** pour gestion dynamique des nœuds
- **Équilibrage de Charge** avec Round-Robin et Least-Connections
- **Intégration CDN** pour actifs statiques

---

**Auteur:** Fahed Mlaiel (mlaiel@live.de)  
**Copyright:** © 2025 Fahed Mlaiel. Tous droits réservés.