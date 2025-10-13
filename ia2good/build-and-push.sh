#!/bin/bash
# Build and Push Docker Images for IA2GOOD Integration
# This script builds all Docker images and pushes them to AWS ECR

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}IA2GOOD Docker Build & Push Script${NC}"
echo -e "${BLUE}========================================${NC}"

# Configuration
AWS_REGION="${AWS_REGION:-eu-central-1}"
AWS_ACCOUNT_ID="${AWS_ACCOUNT_ID:-058264504292}"
ECR_REGISTRY="${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com"
IMAGE_TAG="${IMAGE_TAG:-latest}"

# Microservices to build
SERVICES=("ia2good" "eduverify" "medcare-ai")
declare -A SERVICE_PORTS=(
    ["ia2good"]="8001"
    ["eduverify"]="8002"
    ["medcare-ai"]="8003"
)

echo -e "${YELLOW}Configuration:${NC}"
echo "  AWS Region: ${AWS_REGION}"
echo "  AWS Account: ${AWS_ACCOUNT_ID}"
echo "  ECR Registry: ${ECR_REGISTRY}"
echo "  Image Tag: ${IMAGE_TAG}"
echo ""

# Authenticate with ECR
echo -e "${YELLOW}🔐 Authenticating with AWS ECR...${NC}"
aws ecr get-login-password --region ${AWS_REGION} | docker login --username AWS --password-stdin ${ECR_REGISTRY}
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ ECR authentication successful${NC}"
else
    echo -e "${RED}❌ ECR authentication failed${NC}"
    exit 1
fi

# Create ECR repositories if they don't exist
echo -e "${YELLOW}📦 Creating ECR repositories if needed...${NC}"
for service in "${SERVICES[@]}"; do
    aws ecr describe-repositories --repository-names "ia2good/${service}" --region ${AWS_REGION} 2>/dev/null || \
    aws ecr create-repository --repository-name "ia2good/${service}" --region ${AWS_REGION} --image-scanning-configuration scanOnPush=true
    echo -e "${GREEN}  ✅ Repository ia2good/${service} ready${NC}"
done

# Also create frontend repository
aws ecr describe-repositories --repository-names "ia2good/frontend" --region ${AWS_REGION} 2>/dev/null || \
aws ecr create-repository --repository-name "ia2good/frontend" --region ${AWS_REGION} --image-scanning-configuration scanOnPush=true
echo -e "${GREEN}  ✅ Repository ia2good/frontend ready${NC}"

echo ""

# Build and push backend microservices
echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Building Backend Microservices${NC}"
echo -e "${BLUE}========================================${NC}"

for service in "${SERVICES[@]}"; do
    echo ""
    echo -e "${YELLOW}🏗️  Building ${service} microservice...${NC}"
    
    SERVICE_DIR="microservices/${service}"
    IMAGE_NAME="${ECR_REGISTRY}/ia2good/${service}:${IMAGE_TAG}"
    
    # Build from ia2good root (so we can COPY ../../shared-services)
    docker build \
        -t ${IMAGE_NAME} \
        -f ${SERVICE_DIR}/Dockerfile \
        --build-arg SERVICE_PORT=${SERVICE_PORTS[$service]} \
        .
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ Built ${service} successfully${NC}"
        
        # Push to ECR
        echo -e "${YELLOW}📤 Pushing ${service} to ECR...${NC}"
        docker push ${IMAGE_NAME}
        
        if [ $? -eq 0 ]; then
            echo -e "${GREEN}✅ Pushed ${service} successfully${NC}"
        else
            echo -e "${RED}❌ Failed to push ${service}${NC}"
            exit 1
        fi
    else
        echo -e "${RED}❌ Failed to build ${service}${NC}"
        exit 1
    fi
done

# Build and push frontend
echo ""
echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Building Frontend${NC}"
echo -e "${BLUE}========================================${NC}"

echo -e "${YELLOW}🏗️  Building frontend...${NC}"
FRONTEND_IMAGE="${ECR_REGISTRY}/ia2good/frontend:${IMAGE_TAG}"

docker build \
    -t ${FRONTEND_IMAGE} \
    -f frontend/Dockerfile \
    frontend/

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Built frontend successfully${NC}"
    
    # Push to ECR
    echo -e "${YELLOW}📤 Pushing frontend to ECR...${NC}"
    docker push ${FRONTEND_IMAGE}
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ Pushed frontend successfully${NC}"
    else
        echo -e "${RED}❌ Failed to push frontend${NC}"
        exit 1
    fi
else
    echo -e "${RED}❌ Failed to build frontend${NC}"
    exit 1
fi

# Summary
echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}✅ All images built and pushed successfully!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo -e "${YELLOW}Images pushed:${NC}"
for service in "${SERVICES[@]}"; do
    echo "  • ${ECR_REGISTRY}/ia2good/${service}:${IMAGE_TAG}"
done
echo "  • ${ECR_REGISTRY}/ia2good/frontend:${IMAGE_TAG}"
echo ""
echo -e "${YELLOW}Next steps:${NC}"
echo "  1. Update Kubernetes manifests with image tags"
echo "  2. kubectl apply -f k8s/"
echo "  3. kubectl get pods -n ia2good"
echo ""
