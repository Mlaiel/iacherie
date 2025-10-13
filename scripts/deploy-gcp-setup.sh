#!/bin/bash
# 🚀 Script de Setup Initial GCP pour IA Chérie
# Auteur: Fahed Mlaiel (mlaiel@live.de)
# Usage: ./scripts/deploy-gcp-setup.sh

set -e

# Couleurs
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}"
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║         🚀 IA CHÉRIE - GOOGLE CLOUD SETUP                    ║"
echo "║         Déploiement Automatisé avec GPU                      ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo -e "${NC}"

# Variables (MODIFIEZ SELON VOS BESOINS)
export PROJECT_ID="${GCP_PROJECT_ID:-iacherie-production}"
export REGION="${GCP_REGION:-europe-west1}"
export ZONE="${REGION}-b"
export CLUSTER_NAME="iacherie-cluster"

echo -e "${YELLOW}📋 Configuration:${NC}"
echo "   Project ID: $PROJECT_ID"
echo "   Region: $REGION"
echo "   Cluster: $CLUSTER_NAME"
echo ""

read -p "Voulez-vous continuer ? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${RED}❌ Annulé${NC}"
    exit 1
fi

# 1. Créer/Sélectionner Projet
echo -e "${BLUE}📦 Étape 1/8: Configuration du projet GCP${NC}"
if gcloud projects describe $PROJECT_ID &>/dev/null; then
    echo -e "${GREEN}✅ Projet $PROJECT_ID existe déjà${NC}"
else
    echo -e "${YELLOW}⏳ Création du projet $PROJECT_ID...${NC}"
    gcloud projects create $PROJECT_ID --name="IA Chérie Production"
fi

gcloud config set project $PROJECT_ID
echo -e "${GREEN}✅ Projet configuré${NC}"

# 2. Activer APIs
echo -e "${BLUE}🔌 Étape 2/8: Activation des APIs GCP${NC}"
APIS=(
    "container.googleapis.com"
    "compute.googleapis.com"
    "storage-api.googleapis.com"
    "containerregistry.googleapis.com"
    "dns.googleapis.com"
    "certificatemanager.googleapis.com"
    "monitoring.googleapis.com"
    "logging.googleapis.com"
    "cloudtrace.googleapis.com"
)

for api in "${APIS[@]}"; do
    echo -e "${YELLOW}⏳ Activation: $api${NC}"
    gcloud services enable $api --quiet
done
echo -e "${GREEN}✅ APIs activées (${#APIS[@]}/${#APIS[@]})${NC}"

# 3. Créer Cluster GKE
echo -e "${BLUE}☸️  Étape 3/8: Création du cluster GKE (10-15 min)${NC}"
if gcloud container clusters describe $CLUSTER_NAME --region=$REGION &>/dev/null; then
    echo -e "${GREEN}✅ Cluster $CLUSTER_NAME existe déjà${NC}"
else
    echo -e "${YELLOW}⏳ Création du cluster principal...${NC}"
    gcloud container clusters create $CLUSTER_NAME \
        --project=$PROJECT_ID \
        --region=$REGION \
        --machine-type=n1-standard-4 \
        --num-nodes=1 \
        --enable-autoscaling \
        --min-nodes=1 \
        --max-nodes=10 \
        --enable-autorepair \
        --enable-autoupgrade \
        --enable-ip-alias \
        --network=default \
        --subnetwork=default \
        --enable-stackdriver-kubernetes \
        --enable-cloud-logging \
        --enable-cloud-monitoring \
        --addons=HorizontalPodAutoscaling,HttpLoadBalancing,GcePersistentDiskCsiDriver \
        --workload-pool=$PROJECT_ID.svc.id.goog \
        --enable-shielded-nodes \
        --shielded-secure-boot \
        --shielded-integrity-monitoring \
        --quiet
    
    echo -e "${GREEN}✅ Cluster créé${NC}"
fi

# 4. Ajouter Node Pool GPU
echo -e "${BLUE}🎮 Étape 4/8: Ajout du node pool GPU${NC}"
if gcloud container node-pools describe gpu-pool --cluster=$CLUSTER_NAME --region=$REGION &>/dev/null; then
    echo -e "${GREEN}✅ Node pool GPU existe déjà${NC}"
else
    echo -e "${YELLOW}⏳ Création du node pool GPU (NVIDIA Tesla T4, preemptible)...${NC}"
    gcloud container node-pools create gpu-pool \
        --cluster=$CLUSTER_NAME \
        --region=$REGION \
        --machine-type=n1-standard-4 \
        --accelerator=type=nvidia-tesla-t4,count=1 \
        --num-nodes=0 \
        --enable-autoscaling \
        --min-nodes=0 \
        --max-nodes=3 \
        --disk-size=100 \
        --disk-type=pd-ssd \
        --node-labels=workload=gpu,gpu-type=nvidia-t4 \
        --node-taints=nvidia.com/gpu=present:NoSchedule \
        --enable-autorepair \
        --enable-autoupgrade \
        --preemptible \
        --quiet
    
    echo -e "${GREEN}✅ Node pool GPU créé (économie 69% avec preemptible)${NC}"
fi

# 5. Configurer kubectl
echo -e "${BLUE}⚙️  Étape 5/8: Configuration de kubectl${NC}"
gcloud container clusters get-credentials $CLUSTER_NAME --region=$REGION
echo -e "${GREEN}✅ kubectl configuré${NC}"

# 6. Installer NVIDIA GPU Drivers
echo -e "${BLUE}🎮 Étape 6/8: Installation des drivers NVIDIA${NC}"
kubectl apply -f https://raw.githubusercontent.com/GoogleCloudPlatform/container-engine-accelerators/master/nvidia-driver-installer/cos/daemonset-preloaded-latest.yaml
echo -e "${GREEN}✅ Drivers NVIDIA installés${NC}"

# 7. Créer Service Account pour GitHub Actions
echo -e "${BLUE}🔑 Étape 7/8: Création du service account CI/CD${NC}"
SA_NAME="github-actions"
SA_EMAIL="$SA_NAME@$PROJECT_ID.iam.gserviceaccount.com"

if gcloud iam service-accounts describe $SA_EMAIL &>/dev/null; then
    echo -e "${GREEN}✅ Service account existe déjà${NC}"
else
    echo -e "${YELLOW}⏳ Création du service account...${NC}"
    gcloud iam service-accounts create $SA_NAME \
        --display-name="GitHub Actions Deployer" \
        --quiet
fi

# Donner permissions
echo -e "${YELLOW}⏳ Attribution des rôles IAM...${NC}"
ROLES=(
    "roles/container.developer"
    "roles/storage.admin"
    "roles/iam.serviceAccountUser"
)

for role in "${ROLES[@]}"; do
    gcloud projects add-iam-policy-binding $PROJECT_ID \
        --member="serviceAccount:$SA_EMAIL" \
        --role="$role" \
        --quiet
done

# Créer clé JSON
KEY_FILE="github-actions-key.json"
if [ -f "$KEY_FILE" ]; then
    echo -e "${YELLOW}⚠️  Clé existante trouvée, création d'une nouvelle...${NC}"
    rm -f $KEY_FILE
fi

gcloud iam service-accounts keys create $KEY_FILE \
    --iam-account=$SA_EMAIL \
    --quiet

echo -e "${GREEN}✅ Service account créé${NC}"
echo -e "${YELLOW}⚠️  IMPORTANT: Ajouter le contenu de $KEY_FILE dans GitHub Secret: GCP_SERVICE_ACCOUNT_KEY${NC}"

# 8. Installer NGINX Ingress Controller
echo -e "${BLUE}🌐 Étape 8/8: Installation de NGINX Ingress${NC}"
if kubectl get namespace ingress-nginx &>/dev/null; then
    echo -e "${GREEN}✅ NGINX Ingress déjà installé${NC}"
else
    echo -e "${YELLOW}⏳ Installation de NGINX Ingress via Helm...${NC}"
    helm repo add ingress-nginx https://kubernetes.github.io/ingress-nginx
    helm repo update
    
    helm install ingress-nginx ingress-nginx/ingress-nginx \
        --namespace ingress-nginx \
        --create-namespace \
        --set controller.service.type=LoadBalancer \
        --wait
    
    echo -e "${GREEN}✅ NGINX Ingress installé${NC}"
fi

# Obtenir IP publique
echo -e "${BLUE}🌍 Récupération de l'IP publique...${NC}"
sleep 30  # Attendre que le LoadBalancer soit prêt
EXTERNAL_IP=$(kubectl get svc -n ingress-nginx ingress-nginx-controller -o jsonpath='{.status.loadBalancer.ingress[0].ip}')

if [ -z "$EXTERNAL_IP" ]; then
    echo -e "${YELLOW}⏳ LoadBalancer en cours de création, attente...${NC}"
    kubectl wait --namespace ingress-nginx \
        --for=condition=ready pod \
        --selector=app.kubernetes.io/component=controller \
        --timeout=300s
    
    EXTERNAL_IP=$(kubectl get svc -n ingress-nginx ingress-nginx-controller -o jsonpath='{.status.loadBalancer.ingress[0].ip}')
fi

echo ""
echo -e "${GREEN}╔══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║            🎉 SETUP GCP TERMINÉ AVEC SUCCÈS !                ║${NC}"
echo -e "${GREEN}╚══════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${BLUE}📋 Récapitulatif:${NC}"
echo "   ✅ Projet GCP: $PROJECT_ID"
echo "   ✅ Cluster GKE: $CLUSTER_NAME"
echo "   ✅ Region: $REGION"
echo "   ✅ Node Pool GPU: gpu-pool (NVIDIA T4, preemptible)"
echo "   ✅ NGINX Ingress: Installé"
echo "   🌍 IP Publique: $EXTERNAL_IP"
echo ""
echo -e "${YELLOW}📝 PROCHAINES ÉTAPES:${NC}"
echo ""
echo -e "${BLUE}1. Configurer DNS pour vos 4 domaines:${NC}"
echo "   Ajouter A Records pointant vers: $EXTERNAL_IP"
echo "   - *.iacherie.com → $EXTERNAL_IP"
echo "   - *.iacherie.eu → $EXTERNAL_IP"
echo "   - *.iacherie.de → $EXTERNAL_IP"
echo "   - *.iacherie.online → $EXTERNAL_IP"
echo ""
echo -e "${BLUE}2. Ajouter GitHub Secrets:${NC}"
echo "   Repository: https://github.com/Mlaiel/Ainfluencer/settings/secrets/actions"
echo "   "
echo "   GCP_PROJECT_ID = $PROJECT_ID"
echo "   GCP_SERVICE_ACCOUNT_KEY = (contenu de $KEY_FILE)"
echo ""
echo -e "${BLUE}3. Déployer l'application:${NC}"
echo "   ./scripts/deploy-gcp-app.sh"
echo ""
echo -e "${YELLOW}💰 Estimation des coûts:${NC}"
echo "   - Cluster CPU (1 node): ~$137/mois"
echo "   - GPU T4 Preemptible (0-3 nodes): ~$79/mois par node"
echo "   - Load Balancer: ~$18/mois"
echo "   - Total estimé: ~$234-470/mois selon usage GPU"
echo ""
echo -e "${GREEN}🔑 Clé service account sauvegardée dans: $KEY_FILE${NC}"
echo -e "${RED}⚠️  ATTENTION: Ne committez JAMAIS cette clé dans Git !${NC}"
echo ""
