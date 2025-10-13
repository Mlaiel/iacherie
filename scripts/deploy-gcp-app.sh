#!/bin/bash
# 🚀 Script de Déploiement Application sur GCP
# Auteur: Fahed Mlaiel (mlaiel@live.de)
# Usage: ./scripts/deploy-gcp-app.sh

set -e

# Couleurs
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}"
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║         🚀 IA CHÉRIE - DÉPLOIEMENT APPLICATION               ║"
echo "║         Backend + Frontend + GPU + SSL                       ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo -e "${NC}"

# Variables
export PROJECT_ID="${GCP_PROJECT_ID:-iacherie-production}"
export REGION="${GCP_REGION:-europe-west1}"
export CLUSTER_NAME="iacherie-cluster"
export NAMESPACE="iacherie"

echo -e "${YELLOW}📋 Configuration:${NC}"
echo "   Project: $PROJECT_ID"
echo "   Cluster: $CLUSTER_NAME"
echo "   Namespace: $NAMESPACE"
echo ""

# Vérifier connexion GCP
if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" | grep -q .; then
    echo -e "${RED}❌ Vous n'êtes pas authentifié sur GCP${NC}"
    echo -e "${YELLOW}Exécutez: gcloud auth login${NC}"
    exit 1
fi

# Configurer kubectl
echo -e "${BLUE}⚙️  Configuration de kubectl...${NC}"
gcloud container clusters get-credentials $CLUSTER_NAME --region=$REGION --project=$PROJECT_ID
echo -e "${GREEN}✅ kubectl configuré${NC}"

# 1. Créer Namespace
echo -e "${BLUE}📦 Étape 1/7: Création du namespace${NC}"
kubectl create namespace $NAMESPACE --dry-run=client -o yaml | kubectl apply -f -
echo -e "${GREEN}✅ Namespace créé${NC}"

# 2. Build et Push Docker Image
echo -e "${BLUE}🐳 Étape 2/7: Build et push de l'image Docker${NC}"
IMAGE_NAME="gcr.io/$PROJECT_ID/iacherie-backend"
IMAGE_TAG=$(git rev-parse --short HEAD || echo "latest")
IMAGE_FULL="$IMAGE_NAME:$IMAGE_TAG"

echo -e "${YELLOW}⏳ Configuration de Docker pour GCR...${NC}"
gcloud auth configure-docker --quiet

echo -e "${YELLOW}⏳ Build de l'image: $IMAGE_FULL${NC}"
docker build -f Dockerfile.production -t $IMAGE_FULL -t $IMAGE_NAME:latest .

echo -e "${YELLOW}⏳ Push vers GCR...${NC}"
docker push $IMAGE_FULL
docker push $IMAGE_NAME:latest
echo -e "${GREEN}✅ Image publiée: $IMAGE_FULL${NC}"

# 3. Créer ConfigMap & Secrets
echo -e "${BLUE}🔐 Étape 3/7: Configuration des secrets${NC}"

# ConfigMap pour variables d'environnement
kubectl create configmap iacherie-config \
    --from-literal=ENVIRONMENT=production \
    --from-literal=ENABLE_INTERNAL_MODELS=true \
    --from-literal=GPU_ENABLED=true \
    --namespace=$NAMESPACE \
    --dry-run=client -o yaml | kubectl apply -f -

# Secrets (à personnaliser)
kubectl create secret generic iacherie-secrets \
    --from-literal=DATABASE_URL="postgresql://user:pass@host:5432/db" \
    --from-literal=OPENAI_API_KEY="${OPENAI_API_KEY:-your-key}" \
    --from-literal=LEONARDO_API_KEY="${LEONARDO_API_KEY:-your-key}" \
    --namespace=$NAMESPACE \
    --dry-run=client -o yaml | kubectl apply -f -

echo -e "${GREEN}✅ Secrets configurés${NC}"

# 4. Déployer Application avec GPU
echo -e "${BLUE}🎮 Étape 4/7: Déploiement de l'application avec GPU${NC}"

cat <<EOF | kubectl apply -f -
apiVersion: apps/v1
kind: Deployment
metadata:
  name: stable-diffusion-api
  namespace: $NAMESPACE
  labels:
    app: stable-diffusion
    tier: ai-inference
spec:
  replicas: 1
  selector:
    matchLabels:
      app: stable-diffusion
  template:
    metadata:
      labels:
        app: stable-diffusion
    spec:
      nodeSelector:
        workload: gpu
        gpu-type: nvidia-t4
      tolerations:
      - key: nvidia.com/gpu
        operator: Exists
        effect: NoSchedule
      
      containers:
      - name: backend
        image: $IMAGE_FULL
        ports:
        - containerPort: 8000
          name: http
        
        resources:
          requests:
            cpu: "2"
            memory: "8Gi"
            nvidia.com/gpu: "1"
          limits:
            cpu: "4"
            memory: "16Gi"
            nvidia.com/gpu: "1"
        
        env:
        - name: ENABLE_INTERNAL_MODELS
          value: "true"
        - name: GPU_ENABLED
          value: "true"
        - name: CUDA_VISIBLE_DEVICES
          value: "0"
        - name: TORCH_HOME
          value: "/app/models"
        
        envFrom:
        - configMapRef:
            name: iacherie-config
        - secretRef:
            name: iacherie-secrets
        
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 120
          periodSeconds: 30
        
        readinessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 60
          periodSeconds: 10
        
        volumeMounts:
        - name: model-cache
          mountPath: /app/models
        - name: shm
          mountPath: /dev/shm
      
      volumes:
      - name: model-cache
        persistentVolumeClaim:
          claimName: model-cache-pvc
      - name: shm
        emptyDir:
          medium: Memory
          sizeLimit: 2Gi

---
apiVersion: v1
kind: Service
metadata:
  name: stable-diffusion-service
  namespace: $NAMESPACE
spec:
  selector:
    app: stable-diffusion
  ports:
  - port: 80
    targetPort: 8000
  type: ClusterIP

---
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: model-cache-pvc
  namespace: $NAMESPACE
spec:
  accessModes:
  - ReadWriteOnce
  resources:
    requests:
      storage: 50Gi
  storageClassName: standard-rwo
EOF

echo -e "${GREEN}✅ Déploiement créé${NC}"

# 5. Installer cert-manager pour SSL
echo -e "${BLUE}🔐 Étape 5/7: Installation de cert-manager${NC}"
if kubectl get namespace cert-manager &>/dev/null; then
    echo -e "${GREEN}✅ cert-manager déjà installé${NC}"
else
    echo -e "${YELLOW}⏳ Installation de cert-manager via Helm...${NC}"
    helm repo add jetstack https://charts.jetstack.io
    helm repo update
    
    helm install cert-manager jetstack/cert-manager \
        --namespace cert-manager \
        --create-namespace \
        --version v1.13.0 \
        --set installCRDs=true \
        --wait
    
    echo -e "${GREEN}✅ cert-manager installé${NC}"
fi

# 6. Configurer Let's Encrypt
echo -e "${BLUE}🔐 Étape 6/7: Configuration Let's Encrypt${NC}"

cat <<EOF | kubectl apply -f -
apiVersion: cert-manager.io/v1
kind: ClusterIssuer
metadata:
  name: letsencrypt-prod
spec:
  acme:
    server: https://acme-v02.api.letsencrypt.org/directory
    email: mlaiel@live.de
    privateKeySecretRef:
      name: letsencrypt-prod-key
    solvers:
    - http01:
        ingress:
          class: nginx
EOF

echo -e "${GREEN}✅ Let's Encrypt configuré${NC}"

# 7. Créer Ingress Multi-Domaines avec SSL
echo -e "${BLUE}🌐 Étape 7/7: Configuration Ingress multi-domaines${NC}"

cat <<EOF | kubectl apply -f -
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: iacherie-multi-domain
  namespace: $NAMESPACE
  annotations:
    kubernetes.io/ingress.class: "nginx"
    cert-manager.io/cluster-issuer: "letsencrypt-prod"
    nginx.ingress.kubernetes.io/ssl-redirect: "true"
    nginx.ingress.kubernetes.io/force-ssl-redirect: "true"
    nginx.ingress.kubernetes.io/proxy-body-size: "100m"
    nginx.ingress.kubernetes.io/proxy-read-timeout: "300"
spec:
  tls:
  - hosts:
    - www.iacherie.com
    - api.iacherie.com
    - iacherie.com
    secretName: iacherie-com-tls
  - hosts:
    - www.iacherie.eu
    - api.iacherie.eu
    - iacherie.eu
    secretName: iacherie-eu-tls
  - hosts:
    - www.iacherie.de
    - api.iacherie.de
    - iacherie.de
    secretName: iacherie-de-tls
  - hosts:
    - www.iacherie.online
    - api.iacherie.online
    - iacherie.online
    secretName: iacherie-online-tls
  
  rules:
  - host: api.iacherie.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: stable-diffusion-service
            port:
              number: 80
  
  - host: api.iacherie.eu
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: stable-diffusion-service
            port:
              number: 80
  
  - host: api.iacherie.de
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: stable-diffusion-service
            port:
              number: 80
  
  - host: api.iacherie.online
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: stable-diffusion-service
            port:
              number: 80
EOF

echo -e "${GREEN}✅ Ingress créé${NC}"

# Attendre déploiement
echo -e "${BLUE}⏳ Attente du déploiement...${NC}"
kubectl rollout status deployment/stable-diffusion-api -n $NAMESPACE --timeout=10m

# Afficher résultats
echo ""
echo -e "${GREEN}╔══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║         🎉 DÉPLOIEMENT TERMINÉ AVEC SUCCÈS !                 ║${NC}"
echo -e "${GREEN}╚══════════════════════════════════════════════════════════════╝${NC}"
echo ""

# IP publique
EXTERNAL_IP=$(kubectl get svc -n ingress-nginx ingress-nginx-controller -o jsonpath='{.status.loadBalancer.ingress[0].ip}')
echo -e "${BLUE}🌍 IP Publique du Load Balancer:${NC}"
echo "   $EXTERNAL_IP"
echo ""

# Pods
echo -e "${BLUE}📦 Pods déployés:${NC}"
kubectl get pods -n $NAMESPACE

echo ""
echo -e "${BLUE}🔐 Certificats SSL (attendre 2-5 min):${NC}"
kubectl get certificate -n $NAMESPACE

echo ""
echo -e "${YELLOW}📝 PROCHAINES ÉTAPES:${NC}"
echo ""
echo -e "${BLUE}1. Vérifier DNS:${NC}"
echo "   Assurez-vous que vos domaines pointent vers: $EXTERNAL_IP"
echo ""
echo -e "${BLUE}2. Attendre certificats SSL:${NC}"
echo "   kubectl get certificate -n $NAMESPACE --watch"
echo "   (Ctrl+C pour arrêter)"
echo ""
echo -e "${BLUE}3. Tester l'API:${NC}"
echo "   curl -I https://api.iacherie.com/health"
echo "   curl -X POST https://api.iacherie.com/api/generate/image \\"
echo "     -H 'Content-Type: application/json' \\"
echo "     -d '{\"prompt\":\"un chat\",\"model\":\"internal-sdxl-turbo\"}'"
echo ""
echo -e "${BLUE}4. Voir les logs:${NC}"
echo "   kubectl logs -n $NAMESPACE -l app=stable-diffusion --tail=100 -f"
echo ""
echo -e "${BLUE}5. Tester GPU:${NC}"
echo "   POD=\$(kubectl get pod -n $NAMESPACE -l app=stable-diffusion -o jsonpath='{.items[0].metadata.name}')"
echo "   kubectl exec -n $NAMESPACE \$POD -- nvidia-smi"
echo ""
echo -e "${GREEN}✅ Votre application est maintenant en ligne sur GCP avec GPU !${NC}"
echo ""
