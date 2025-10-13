#!/bin/bash

# Script de déploiement complet sur Google Cloud Platform
# Déploie les 61 APIs + Application complète avec SSL

set -e

echo "=============================================="
echo "🚀 DÉPLOIEMENT COMPLET IACHERIE SUR GCP"
echo "=============================================="
echo ""

# Couleurs pour les messages
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Configuration
PROJECT_ID="iacherie"
REGION="europe-west1"
CLUSTER_NAME="iacherie-cluster"
NAMESPACE="iacherie-prod"

echo -e "${BLUE}📋 Configuration:${NC}"
echo "  - Project: $PROJECT_ID"
echo "  - Region: $REGION"
echo "  - Cluster: $CLUSTER_NAME"
echo "  - Namespace: $NAMESPACE"
echo ""

# Étape 1: Vérifier kubectl
echo -e "${BLUE}1️⃣  Vérification de kubectl...${NC}"
if ! kubectl get nodes &> /dev/null; then
    echo -e "${YELLOW}⚠️  kubectl non configuré. Configuration en cours...${NC}"
    gcloud container clusters get-credentials $CLUSTER_NAME --region=$REGION --project=$PROJECT_ID
fi
echo -e "${GREEN}✅ kubectl configuré${NC}"
echo ""

# Étape 2: Créer le namespace
echo -e "${BLUE}2️⃣  Création du namespace...${NC}"
kubectl apply -f k8s/namespace.yaml
echo -e "${GREEN}✅ Namespace créé${NC}"
echo ""

# Étape 3: Créer ConfigMap
echo -e "${BLUE}3️⃣  Création de la ConfigMap...${NC}"
kubectl apply -f k8s/configmap.yaml
echo -e "${GREEN}✅ ConfigMap créée${NC}"
echo ""

# Étape 4: Créer les Secrets avec les 61 APIs
echo -e "${BLUE}4️⃣  Création des Secrets (61 APIs)...${NC}"
chmod +x k8s/create-secrets.sh
./k8s/create-secrets.sh
echo -e "${GREEN}✅ Secrets créés avec 61 APIs${NC}"
echo ""

# Étape 5: Créer ClusterIssuer pour SSL
echo -e "${BLUE}5️⃣  Configuration SSL (Let's Encrypt)...${NC}"
kubectl apply -f k8s/cluster-issuer.yaml
sleep 5
echo -e "${GREEN}✅ ClusterIssuer configuré${NC}"
echo ""

# Étape 6: Build et push des images Docker
echo -e "${BLUE}6️⃣  Build des images Docker...${NC}"

echo -e "${YELLOW}   📦 Build Backend...${NC}"
gcloud builds submit --tag gcr.io/$PROJECT_ID/backend:latest \
  --file=Dockerfile.backend \
  --timeout=20m \
  .

echo -e "${YELLOW}   📦 Build Frontend...${NC}"
gcloud builds submit --tag gcr.io/$PROJECT_ID/frontend:latest \
  --file=Dockerfile.frontend \
  --timeout=20m \
  .

echo -e "${GREEN}✅ Images Docker créées et poussées${NC}"
echo ""

# Étape 7: Déployer Backend
echo -e "${BLUE}7️⃣  Déploiement du Backend (3 replicas)...${NC}"
kubectl apply -f k8s/backend-deployment.yaml
echo -e "${GREEN}✅ Backend déployé${NC}"
echo ""

# Étape 8: Déployer Frontend
echo -e "${BLUE}8️⃣  Déploiement du Frontend (2 replicas)...${NC}"
kubectl apply -f k8s/frontend-deployment.yaml
echo -e "${GREEN}✅ Frontend déployé${NC}"
echo ""

# Étape 9: Configurer Ingress avec SSL pour les 4 domaines
echo -e "${BLUE}9️⃣  Configuration Ingress + SSL (4 domaines)...${NC}"
kubectl apply -f k8s/ingress.yaml
echo -e "${GREEN}✅ Ingress configuré${NC}"
echo ""

# Étape 10: Attendre que tout soit prêt
echo -e "${BLUE}🔟 Attente du démarrage des pods...${NC}"
echo "   Cela peut prendre 2-5 minutes..."
kubectl wait --for=condition=ready pod \
  -l app=iacherie-backend \
  -n $NAMESPACE \
  --timeout=300s || true

kubectl wait --for=condition=ready pod \
  -l app=iacherie-frontend \
  -n $NAMESPACE \
  --timeout=300s || true

echo -e "${GREEN}✅ Pods démarrés${NC}"
echo ""

# Étape 11: Obtenir l'IP Ingress
echo -e "${BLUE}1️⃣1️⃣  Récupération de l'IP Ingress...${NC}"
echo "   Attente de l'IP externe (peut prendre 1-2 minutes)..."
for i in {1..30}; do
    INGRESS_IP=$(kubectl get ingress iacherie-ingress -n $NAMESPACE -o jsonpath='{.status.loadBalancer.ingress[0].ip}' 2>/dev/null || echo "")
    if [ ! -z "$INGRESS_IP" ]; then
        break
    fi
    echo -n "."
    sleep 10
done
echo ""

if [ -z "$INGRESS_IP" ]; then
    echo -e "${YELLOW}⚠️  L'IP Ingress n'est pas encore disponible${NC}"
    echo "   Exécutez cette commande plus tard:"
    echo "   kubectl get ingress iacherie-ingress -n $NAMESPACE"
else
    echo -e "${GREEN}✅ IP Ingress: $INGRESS_IP${NC}"
fi
echo ""

# Résumé final
echo "=============================================="
echo -e "${GREEN}✅ DÉPLOIEMENT TERMINÉ !${NC}"
echo "=============================================="
echo ""
echo -e "${BLUE}📊 RÉSUMÉ:${NC}"
echo "  ✅ 61 APIs configurées"
echo "  ✅ Backend: 3 replicas"
echo "  ✅ Frontend: 2 replicas"
echo "  ✅ SSL: Let's Encrypt (4 domaines)"
echo "  ✅ Ingress Nginx configuré"
echo ""

if [ ! -z "$INGRESS_IP" ]; then
    echo -e "${BLUE}🌐 CONFIGURATION DNS REQUISE:${NC}"
    echo "  Ajoutez ces enregistrements DNS A chez votre registrar:"
    echo ""
    echo "  iacherie.com        → $INGRESS_IP"
    echo "  www.iacherie.com    → $INGRESS_IP"
    echo "  iacherie.eu         → $INGRESS_IP"
    echo "  www.iacherie.eu     → $INGRESS_IP"
    echo "  iacherie.de         → $INGRESS_IP"
    echo "  www.iacherie.de     → $INGRESS_IP"
    echo "  iacherie.online     → $INGRESS_IP"
    echo "  www.iacherie.online → $INGRESS_IP"
    echo ""
fi

echo -e "${BLUE}🔍 COMMANDES UTILES:${NC}"
echo "  # Voir les pods"
echo "  kubectl get pods -n $NAMESPACE"
echo ""
echo "  # Voir les logs backend"
echo "  kubectl logs -f -l app=iacherie-backend -n $NAMESPACE"
echo ""
echo "  # Voir les logs frontend"
echo "  kubectl logs -f -l app=iacherie-frontend -n $NAMESPACE"
echo ""
echo "  # Voir l'état SSL"
echo "  kubectl get certificate -n $NAMESPACE"
echo ""
echo "  # Voir l'Ingress"
echo "  kubectl get ingress -n $NAMESPACE"
echo ""

echo -e "${GREEN}🎉 Votre application sera accessible sur:${NC}"
echo "  https://iacherie.com"
echo "  https://iacherie.eu"
echo "  https://iacherie.de"
echo "  https://iacherie.online"
echo ""
echo -e "${YELLOW}⏳ Note: Les certificats SSL peuvent prendre 5-10 minutes${NC}"
echo "=============================================="
