# 🚀 DÉMARRAGE RAPIDE - DÉPLOIEMENT GCP

**⏱️ Temps estimé**: 30-45 minutes  
**💰 Coût**: ~$370-577/mois selon usage GPU

---

## 📋 PRÉREQUIS (5 min)

1. **Compte Google Cloud Platform**
   - Créer sur: https://console.cloud.google.com
   - Activer la facturation
   - Obtenir $300 de crédits gratuits (nouveaux comptes)

2. **Outils CLI installés**
   ```bash
   # Google Cloud SDK
   curl https://sdk.cloud.google.com | bash
   exec -l $SHELL
   gcloud init
   
   # kubectl
   gcloud components install kubectl
   
   # Helm
   curl https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash
   ```

3. **Domaines configurés** (déjà fait ✅)
   - iacherie.com
   - iacherie.eu
   - iacherie.de
   - iacherie.online

---

## 🚀 DÉPLOIEMENT EN 3 COMMANDES

### Étape 1: Setup Infrastructure GCP (15 min)
```bash
# Rendre le script exécutable
chmod +x scripts/deploy-gcp-setup.sh

# Lancer le setup
./scripts/deploy-gcp-setup.sh
```

**Ce que fait le script:**
- ✅ Crée le projet GCP
- ✅ Active les APIs nécessaires
- ✅ Crée le cluster Kubernetes (GKE)
- ✅ Ajoute le node pool GPU (NVIDIA T4)
- ✅ Installe les drivers NVIDIA
- ✅ Configure le service account pour CI/CD
- ✅ Installe NGINX Ingress Controller
- ✅ Récupère l'IP publique

**Résultat attendu:**
```
✅ Projet GCP: iacherie-production
✅ Cluster GKE: iacherie-cluster
✅ Node Pool GPU: gpu-pool (NVIDIA T4)
🌍 IP Publique: XX.XX.XX.XX
```

### Étape 2: Configurer DNS (5 min)

Aller sur votre registrar de domaine et ajouter des A Records:

```
Type  Name  Value              TTL
A     @     XX.XX.XX.XX        3600
A     www   XX.XX.XX.XX        3600
A     api   XX.XX.XX.XX        3600
```

**Pour les 4 domaines:**
- iacherie.com
- iacherie.eu
- iacherie.de
- iacherie.online

**Vérifier DNS (attendre 5-10 min):**
```bash
dig api.iacherie.com +short
# Devrait retourner: XX.XX.XX.XX
```

### Étape 3: Déployer l'Application (10 min)
```bash
# Configurer variables d'environnement
export GCP_PROJECT_ID="iacherie-production"
export OPENAI_API_KEY="sk-..." # Si vous utilisez DALL-E
export LEONARDO_API_KEY="..."  # Si vous utilisez Leonardo

# Rendre le script exécutable
chmod +x scripts/deploy-gcp-app.sh

# Déployer
./scripts/deploy-gcp-app.sh
```

**Ce que fait le script:**
- ✅ Crée le namespace Kubernetes
- ✅ Build et push l'image Docker vers GCR
- ✅ Configure les secrets et ConfigMaps
- ✅ Déploie l'application avec GPU
- ✅ Installe cert-manager pour SSL
- ✅ Configure Let's Encrypt
- ✅ Crée l'Ingress multi-domaines
- ✅ Attend que le déploiement soit prêt

**Résultat attendu:**
```
✅ Déploiement créé
✅ Image publiée: gcr.io/iacherie-production/iacherie-backend:abc123
✅ Certificats SSL en cours de génération...
```

---

## 🔐 CONFIGURER CI/CD GITHUB (5 min)

### 1. Copier la clé service account
```bash
cat github-actions-key.json | pbcopy  # macOS
cat github-actions-key.json | xclip   # Linux
```

### 2. Ajouter les Secrets GitHub
Aller sur: `https://github.com/Mlaiel/Ainfluencer/settings/secrets/actions`

Cliquer **"New repository secret"** et ajouter:

| Nom | Valeur |
|-----|--------|
| `GCP_PROJECT_ID` | `iacherie-production` |
| `GCP_SERVICE_ACCOUNT_KEY` | *Coller le contenu de github-actions-key.json* |
| `SLACK_WEBHOOK_URL` | *(Optionnel)* URL webhook Slack |

### 3. Activer GitHub Actions
```bash
# Commit le workflow
git add .github/workflows/gcp-deploy.yml
git commit -m "🚀 Add GCP deployment workflow"
git push origin main
```

**✅ Maintenant, chaque push sur `main` déploie automatiquement !**

---

## ✅ VÉRIFICATION (5 min)

### 1. Vérifier les Pods
```bash
kubectl get pods -n iacherie
```

**Attendu:**
```
NAME                                   READY   STATUS    RESTARTS   AGE
stable-diffusion-api-xxxxxxxxx-xxxxx   1/1     Running   0          5m
```

### 2. Vérifier les Certificats SSL
```bash
kubectl get certificate -n iacherie
```

**Attendu (après 2-5 min):**
```
NAME                  READY   SECRET                AGE
iacherie-com-tls      True    iacherie-com-tls      5m
iacherie-eu-tls       True    iacherie-eu-tls       5m
iacherie-de-tls       True    iacherie-de-tls       5m
iacherie-online-tls   True    iacherie-online-tls   5m
```

### 3. Tester l'API
```bash
# Health check
curl -I https://api.iacherie.com/health

# Génération d'image
curl -X POST https://api.iacherie.com/api/generate/image \
  -H 'Content-Type: application/json' \
  -d '{
    "prompt": "un chat mignon avec des lunettes de soleil",
    "model": "internal-sdxl-turbo"
  }'
```

**Attendu:**
```json
{
  "success": true,
  "data": {
    "url": "https://storage.googleapis.com/...",
    "model": "internal-sdxl-turbo",
    "cost": 0.0,
    "generation_time": 3.2
  }
}
```

### 4. Vérifier GPU
```bash
# Obtenir le nom du pod
POD=$(kubectl get pod -n iacherie -l app=stable-diffusion -o jsonpath='{.items[0].metadata.name}')

# Tester GPU
kubectl exec -n iacherie $POD -- nvidia-smi
```

**Attendu:**
```
+-----------------------------------------------------------------------------+
| NVIDIA-SMI 525.60.13    Driver Version: 525.60.13    CUDA Version: 12.0   |
|-------------------------------+----------------------+----------------------+
| GPU  Name        Persistence-M| Bus-Id        Disp.A | Volatile Uncorr. ECC |
|   0  Tesla T4            On   | 00000000:00:04.0 Off |                    0 |
+-------------------------------+----------------------+----------------------+
```

### 5. Tester les 4 Domaines
```bash
# Test rapide
for domain in iacherie.com iacherie.eu iacherie.de iacherie.online; do
  echo "Testing https://api.$domain..."
  curl -I https://api.$domain/health 2>&1 | head -1
done
```

**Attendu:**
```
Testing https://api.iacherie.com...
HTTP/2 200
Testing https://api.iacherie.eu...
HTTP/2 200
Testing https://api.iacherie.de...
HTTP/2 200
Testing https://api.iacherie.online...
HTTP/2 200
```

---

## 🎉 FÉLICITATIONS !

Votre plateforme IA Chérie est maintenant **DÉPLOYÉE EN PRODUCTION** sur Google Cloud avec:

✅ **4 domaines HTTPS** avec SSL gratuit auto-renouvelable  
✅ **GPU NVIDIA T4** pour génération d'images internes (SDXL, SD-turbo)  
✅ **CI/CD automatique** GitHub → GCP  
✅ **Auto-scaling** CPU + GPU  
✅ **Monitoring** intégré  
✅ **Zero downtime** déploiement  

---

## 🔧 COMMANDES UTILES

### Logs en temps réel
```bash
kubectl logs -n iacherie -l app=stable-diffusion --tail=100 -f
```

### Redémarrer l'application
```bash
kubectl rollout restart deployment/stable-diffusion-api -n iacherie
```

### Scaler manuellement
```bash
# Augmenter à 2 replicas
kubectl scale deployment stable-diffusion-api -n iacherie --replicas=2
```

### Voir l'historique des déploiements
```bash
kubectl rollout history deployment/stable-diffusion-api -n iacherie
```

### Rollback version précédente
```bash
kubectl rollout undo deployment/stable-diffusion-api -n iacherie
```

### Shell dans le pod
```bash
POD=$(kubectl get pod -n iacherie -l app=stable-diffusion -o jsonpath='{.items[0].metadata.name}')
kubectl exec -it -n iacherie $POD -- bash
```

### Voir les métriques
```bash
# Métriques pods
kubectl top pods -n iacherie

# Métriques nodes
kubectl top nodes

# GPU utilization
kubectl describe node -l workload=gpu | grep -A 10 "Allocated resources"
```

---

## 🆘 DÉPANNAGE

### Certificat SSL ne se génère pas
```bash
# Voir les events cert-manager
kubectl get events -n iacherie --sort-by='.lastTimestamp'

# Logs cert-manager
kubectl logs -n cert-manager -l app=cert-manager --tail=100
```

### Pod ne démarre pas
```bash
# Voir les events
kubectl describe pod -n iacherie -l app=stable-diffusion

# Voir les logs
kubectl logs -n iacherie -l app=stable-diffusion --tail=200
```

### GPU non disponible
```bash
# Vérifier nodes GPU
kubectl get nodes -l workload=gpu

# Scaler le node pool GPU
gcloud container clusters resize iacherie-cluster \
  --node-pool=gpu-pool \
  --num-nodes=1 \
  --region=europe-west1
```

### Rollback d'urgence
```bash
# Rollback immédiat
kubectl rollout undo deployment/stable-diffusion-api -n iacherie
kubectl rollout status deployment/stable-diffusion-api -n iacherie
```

---

## 📊 MONITORING

### Accéder à Grafana (si installé)
```bash
kubectl port-forward -n monitoring svc/prometheus-grafana 3000:80
```

Ouvrir: http://localhost:3000  
User: `admin` / Password: `Admin123!`

### GCP Console
- **Logs**: https://console.cloud.google.com/logs
- **Monitoring**: https://console.cloud.google.com/monitoring
- **Kubernetes**: https://console.cloud.google.com/kubernetes

---

## 💰 OPTIMISATION DES COÛTS

### Scale to Zero GPU (quand pas utilisé)
```bash
# Descendre à 0 replica (GPU)
kubectl scale deployment stable-diffusion-api -n iacherie --replicas=0

# Remonter quand nécessaire
kubectl scale deployment stable-diffusion-api -n iacherie --replicas=1
```

### Utiliser GPU Spot/Preemptible (69% moins cher)
✅ Déjà configuré dans le setup !

### Nettoyer images Docker anciennes
```bash
# Lister images
gcloud container images list --repository=gcr.io/$PROJECT_ID

# Supprimer images > 30 jours
gcloud container images list-tags gcr.io/$PROJECT_ID/iacherie-backend \
  --filter="timestamp.datetime < $(date -d '-30 days' --iso-8601)" \
  --format="get(digest)" \
  | xargs -I {} gcloud container images delete gcr.io/$PROJECT_ID/iacherie-backend@{} --quiet
```

---

## 🎓 PROCHAINES ÉTAPES

1. **Configurer Monitoring Avancé**
   - Installer Prometheus + Grafana
   - Dashboards GPU
   - Alertes Slack

2. **Optimiser Performance**
   - CDN Cloudflare
   - Redis Cache
   - Image optimization

3. **Ajouter Features**
   - Frontend Next.js
   - WebSocket pour temps réel
   - Queue system (Celery)

4. **Sécurité**
   - WAF (Web Application Firewall)
   - Rate limiting avancé
   - DDoS protection

---

## 📞 SUPPORT

**Auteur**: Fahed Mlaiel  
**Email**: mlaiel@live.de  
**GitHub**: https://github.com/Mlaiel/Ainfluencer

**Documentation complète**: [DEPLOIEMENT_GOOGLE_CLOUD_COMPLET.md](./DEPLOIEMENT_GOOGLE_CLOUD_COMPLET.md)

---

**🚀 Bon déploiement !**
