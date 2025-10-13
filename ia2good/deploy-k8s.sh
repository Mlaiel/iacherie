#!/bin/bash
# Deploy IA2GOOD Integration to Kubernetes
# This script deploys all IA2GOOD services to the EKS cluster

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}IA2GOOD Kubernetes Deployment Script${NC}"
echo -e "${BLUE}========================================${NC}"

# Configuration
NAMESPACE="ia2good"
K8S_DIR="k8s"
AWS_REGION="${AWS_REGION:-eu-central-1}"
AWS_ACCOUNT_ID="${AWS_ACCOUNT_ID:-058264504292}"
ECR_REGISTRY="${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com"
IMAGE_TAG="${IMAGE_TAG:-latest}"

echo -e "${YELLOW}Configuration:${NC}"
echo "  Namespace: ${NAMESPACE}"
echo "  K8s manifests: ${K8S_DIR}"
echo "  ECR Registry: ${ECR_REGISTRY}"
echo "  Image Tag: ${IMAGE_TAG}"
echo ""

# Check kubectl connection
echo -e "${YELLOW}🔍 Checking Kubernetes connection...${NC}"
kubectl cluster-info > /dev/null 2>&1
if [ $? -eq 0 ]; then
    CURRENT_CONTEXT=$(kubectl config current-context)
    echo -e "${GREEN}✅ Connected to cluster: ${CURRENT_CONTEXT}${NC}"
else
    echo -e "${RED}❌ Not connected to Kubernetes cluster${NC}"
    echo "   Please run: aws eks update-kubeconfig --name iacherie-cluster --region ${AWS_REGION}"
    exit 1
fi

# Update image references in manifests
echo ""
echo -e "${YELLOW}📝 Updating image references in manifests...${NC}"

# Backup original files
cp ${K8S_DIR}/02-ia2good-api-deployment.yaml ${K8S_DIR}/02-ia2good-api-deployment.yaml.bak
cp ${K8S_DIR}/03-eduverify-api-deployment.yaml ${K8S_DIR}/03-eduverify-api-deployment.yaml.bak
cp ${K8S_DIR}/04-medcare-api-deployment.yaml ${K8S_DIR}/04-medcare-api-deployment.yaml.bak
cp ${K8S_DIR}/06-frontend-deployment.yaml ${K8S_DIR}/06-frontend-deployment.yaml.bak

# Update Guardian API
sed -i "s|image:.*ia2good.*|image: ${ECR_REGISTRY}/ia2good/ia2good:${IMAGE_TAG}|g" ${K8S_DIR}/02-ia2good-api-deployment.yaml

# Update EduVerify API
sed -i "s|image:.*eduverify.*|image: ${ECR_REGISTRY}/ia2good/eduverify:${IMAGE_TAG}|g" ${K8S_DIR}/03-eduverify-api-deployment.yaml

# Update MedCare API
sed -i "s|image:.*medcare.*|image: ${ECR_REGISTRY}/ia2good/medcare-ai:${IMAGE_TAG}|g" ${K8S_DIR}/04-medcare-api-deployment.yaml

# Update Frontend
sed -i "s|image:.*frontend.*|image: ${ECR_REGISTRY}/ia2good/frontend:${IMAGE_TAG}|g" ${K8S_DIR}/06-frontend-deployment.yaml

echo -e "${GREEN}✅ Image references updated${NC}"

# Deploy to Kubernetes
echo ""
echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Deploying to Kubernetes${NC}"
echo -e "${BLUE}========================================${NC}"

# Apply manifests in order
MANIFESTS=(
    "00-namespace.yaml"
    "01-configmap-secrets.yaml"
    "02-ia2good-api-deployment.yaml"
    "03-eduverify-api-deployment.yaml"
    "04-medcare-api-deployment.yaml"
    "06-frontend-deployment.yaml"
    "05-ingress-multi-domains.yaml"
)

for manifest in "${MANIFESTS[@]}"; do
    echo ""
    echo -e "${YELLOW}📦 Applying ${manifest}...${NC}"
    kubectl apply -f ${K8S_DIR}/${manifest}
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ Applied ${manifest}${NC}"
    else
        echo -e "${RED}❌ Failed to apply ${manifest}${NC}"
        exit 1
    fi
    
    # Wait a bit between deployments
    sleep 2
done

# Wait for deployments to be ready
echo ""
echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Waiting for Deployments${NC}"
echo -e "${BLUE}========================================${NC}"

DEPLOYMENTS=("ia2good-api" "eduverify-api" "medcare-api" "ia2good-frontend")

for deployment in "${DEPLOYMENTS[@]}"; do
    echo ""
    echo -e "${YELLOW}⏳ Waiting for ${deployment} to be ready...${NC}"
    kubectl rollout status deployment/${deployment} -n ${NAMESPACE} --timeout=5m
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ ${deployment} is ready${NC}"
    else
        echo -e "${RED}⚠️  ${deployment} rollout timeout (might still be starting)${NC}"
    fi
done

# Display pod status
echo ""
echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Pod Status${NC}"
echo -e "${BLUE}========================================${NC}"
kubectl get pods -n ${NAMESPACE} -o wide

# Display service endpoints
echo ""
echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Service Endpoints${NC}"
echo -e "${BLUE}========================================${NC}"
kubectl get services -n ${NAMESPACE}

# Display ingress
echo ""
echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Ingress Configuration${NC}"
echo -e "${BLUE}========================================${NC}"
kubectl get ingress -n ${NAMESPACE}

# Get ingress external IP
echo ""
echo -e "${YELLOW}🌐 Getting Ingress external IP...${NC}"
INGRESS_IP=$(kubectl get ingress ia2good-multi-domain -n ${NAMESPACE} -o jsonpath='{.status.loadBalancer.ingress[0].hostname}' 2>/dev/null)

if [ ! -z "$INGRESS_IP" ]; then
    echo -e "${GREEN}✅ Ingress endpoint: ${INGRESS_IP}${NC}"
    echo ""
    echo -e "${YELLOW}Configure DNS:${NC}"
    echo "  ia2good.com → ${INGRESS_IP}"
    echo "  www.ia2good.com → ${INGRESS_IP}"
    echo "  volunteer.ia2good.com → ${INGRESS_IP}"
    echo "  eduverify.ia2good.com → ${INGRESS_IP}"
    echo "  medcare.ia2good.com → ${INGRESS_IP}"
    echo "  ia2good.info → ${INGRESS_IP}"
    echo "  ia2good.store → ${INGRESS_IP}"
    echo "  ia2good.de → ${INGRESS_IP}"
else
    echo -e "${YELLOW}⚠️  Ingress external IP not yet assigned (might take a few minutes)${NC}"
fi

# Display logs command
echo ""
echo -e "${YELLOW}📋 View logs:${NC}"
echo "  Guardian: kubectl logs -f deployment/ia2good-api -n ${NAMESPACE}"
echo "  EduVerify: kubectl logs -f deployment/eduverify-api -n ${NAMESPACE}"
echo "  MedCare: kubectl logs -f deployment/medcare-api -n ${NAMESPACE}"
echo "  Frontend: kubectl logs -f deployment/ia2good-frontend -n ${NAMESPACE}"

# Summary
echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}✅ Deployment Complete!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo -e "${YELLOW}Next steps:${NC}"
echo "  1. Monitor pod status: kubectl get pods -n ${NAMESPACE} -w"
echo "  2. Check logs for any errors"
echo "  3. Configure DNS records to point to ingress endpoint"
echo "  4. Verify SSL certificates: kubectl get certificate -n ${NAMESPACE}"
echo "  5. Test endpoints once DNS is configured"
echo ""
echo -e "${YELLOW}Health check URLs (after DNS):${NC}"
echo "  https://ia2good.com/health"
echo "  https://volunteer.ia2good.com/api/guardian/health"
echo "  https://eduverify.ia2good.com/api/eduverify/health"
echo "  https://medcare.ia2good.com/api/medcare/health"
echo ""
