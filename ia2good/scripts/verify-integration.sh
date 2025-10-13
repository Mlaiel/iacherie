#!/bin/bash
# Pre-Deployment Verification Script
# Vérifie que tous les composants sont prêts pour le déploiement

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

ERRORS=0
WARNINGS=0

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}IA2GOOD Pre-Deployment Verification${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Function to check file exists
check_file() {
    local file=$1
    local description=$2
    
    if [ -f "$file" ]; then
        echo -e "${GREEN}✅${NC} ${description}"
        return 0
    else
        echo -e "${RED}❌${NC} ${description} - NOT FOUND: ${file}"
        ((ERRORS++))
        return 1
    fi
}

# Function to check directory exists
check_dir() {
    local dir=$1
    local description=$2
    
    if [ -d "$dir" ]; then
        echo -e "${GREEN}✅${NC} ${description}"
        return 0
    else
        echo -e "${RED}❌${NC} ${description} - NOT FOUND: ${dir}"
        ((ERRORS++))
        return 1
    fi
}

# Function to check port in file
check_port() {
    local file=$1
    local port=$2
    local description=$3
    
    if grep -q "$port" "$file"; then
        echo -e "${GREEN}✅${NC} ${description} (port ${port})"
        return 0
    else
        echo -e "${RED}❌${NC} ${description} - Port ${port} not found in ${file}"
        ((ERRORS++))
        return 1
    fi
}

# =============================================
# 1. CHECK FILE STRUCTURE
# =============================================
echo -e "${BLUE}[1/8] Checking File Structure${NC}"
echo ""

check_dir "microservices/ia2good" "Guardian API directory"
check_dir "microservices/eduverify" "EduVerify API directory"
check_dir "microservices/medcare-ai" "MedCare API directory"
check_dir "frontend" "Frontend directory"
check_dir "shared-services" "Shared services directory"
check_dir "k8s" "Kubernetes manifests directory"
check_dir "database/migrations" "Database migrations directory"

echo ""

# =============================================
# 2. CHECK DOCKERFILES
# =============================================
echo -e "${BLUE}[2/8] Checking Dockerfiles${NC}"
echo ""

check_file "microservices/ia2good/Dockerfile" "Guardian Dockerfile"
check_file "microservices/eduverify/Dockerfile" "EduVerify Dockerfile"
check_file "microservices/medcare-ai/Dockerfile" "MedCare Dockerfile"
check_file "frontend/Dockerfile" "Frontend Dockerfile"

# Check ports in Dockerfiles
check_port "microservices/ia2good/Dockerfile" "8001" "Guardian port"
check_port "microservices/eduverify/Dockerfile" "8002" "EduVerify port"
check_port "microservices/medcare-ai/Dockerfile" "8003" "MedCare port"
check_port "frontend/Dockerfile" "80" "Frontend port"

echo ""

# =============================================
# 3. CHECK SHARED SERVICES
# =============================================
echo -e "${BLUE}[3/8] Checking Shared Services${NC}"
echo ""

check_file "shared-services/iacherie_ai_client.py" "IACherie AI Client"
check_file "shared-services/ai_orchestrator.py" "AI Orchestrator"
check_file "shared-services/requirements.txt" "Shared services requirements"

# Check critical classes/functions
if grep -q "class IAcherieAIClient" shared-services/iacherie_ai_client.py; then
    echo -e "${GREEN}✅${NC} IAcherieAIClient class found"
else
    echo -e "${RED}❌${NC} IAcherieAIClient class not found"
    ((ERRORS++))
fi

if grep -q "class AIOrchestrator" shared-services/ai_orchestrator.py; then
    echo -e "${GREEN}✅${NC} AIOrchestrator class found"
else
    echo -e "${RED}❌${NC} AIOrchestrator class not found"
    ((ERRORS++))
fi

echo ""

# =============================================
# 4. CHECK AI ROUTES
# =============================================
echo -e "${BLUE}[4/8] Checking AI Routes${NC}"
echo ""

check_file "microservices/ia2good/routes/ai_routes.py" "Guardian AI routes"
check_file "microservices/eduverify/routes/ai_routes.py" "EduVerify AI routes"
check_file "microservices/medcare-ai/routes/ai_routes.py" "MedCare AI routes"

# Count endpoints
guardian_endpoints=$(grep -c "^@router\.post\|^@router\.get" microservices/ia2good/routes/ai_routes.py || echo 0)
eduverify_endpoints=$(grep -c "^@router\.post\|^@router\.get" microservices/eduverify/routes/ai_routes.py || echo 0)
medcare_endpoints=$(grep -c "^@router\.post\|^@router\.get" microservices/medcare-ai/routes/ai_routes.py || echo 0)

echo -e "${YELLOW}Guardian endpoints:${NC} ${guardian_endpoints}"
echo -e "${YELLOW}EduVerify endpoints:${NC} ${eduverify_endpoints}"
echo -e "${YELLOW}MedCare endpoints:${NC} ${medcare_endpoints}"
echo -e "${YELLOW}Total AI endpoints:${NC} $((guardian_endpoints + eduverify_endpoints + medcare_endpoints))"

echo ""

# =============================================
# 5. CHECK MAIN.PY INTEGRATIONS
# =============================================
echo -e "${BLUE}[5/8] Checking main.py Integrations${NC}"
echo ""

# Check sys.path manipulation
if grep -q "sys.path.insert.*shared-services" microservices/ia2good/main.py; then
    echo -e "${GREEN}✅${NC} Guardian sys.path configured"
else
    echo -e "${RED}❌${NC} Guardian sys.path not configured"
    ((ERRORS++))
fi

if grep -q "sys.path.insert.*shared-services" microservices/eduverify/main.py; then
    echo -e "${GREEN}✅${NC} EduVerify sys.path configured"
else
    echo -e "${RED}❌${NC} EduVerify sys.path not configured"
    ((ERRORS++))
fi

if grep -q "sys.path.insert.*shared-services" microservices/medcare-ai/main.py; then
    echo -e "${GREEN}✅${NC} MedCare sys.path configured"
else
    echo -e "${RED}❌${NC} MedCare sys.path not configured"
    ((ERRORS++))
fi

# Check AI routes import
if grep -q "from routes import ai_routes" microservices/ia2good/main.py; then
    echo -e "${GREEN}✅${NC} Guardian AI routes imported"
else
    echo -e "${YELLOW}⚠️${NC}  Guardian AI routes not imported"
    ((WARNINGS++))
fi

if grep -q "from routes import ai_routes" microservices/eduverify/main.py; then
    echo -e "${GREEN}✅${NC} EduVerify AI routes imported"
else
    echo -e "${YELLOW}⚠️${NC}  EduVerify AI routes not imported"
    ((WARNINGS++))
fi

if grep -q "from routes import ai_routes" microservices/medcare-ai/main.py; then
    echo -e "${GREEN}✅${NC} MedCare AI routes imported"
else
    echo -e "${YELLOW}⚠️${NC}  MedCare AI routes not imported"
    ((WARNINGS++))
fi

# Check correct ports in main.py
check_port "microservices/ia2good/main.py" "8001" "Guardian main.py port"
check_port "microservices/eduverify/main.py" "8002" "EduVerify main.py port"
check_port "microservices/medcare-ai/main.py" "8003" "MedCare main.py port"

# Check correct prefixes
if grep -q 'prefix="/api/guardian"' microservices/ia2good/main.py; then
    echo -e "${GREEN}✅${NC} Guardian correct API prefix (/api/guardian)"
else
    echo -e "${RED}❌${NC} Guardian wrong API prefix (should be /api/guardian)"
    ((ERRORS++))
fi

if grep -q 'prefix="/api/eduverify"' microservices/eduverify/main.py; then
    echo -e "${GREEN}✅${NC} EduVerify correct API prefix (/api/eduverify)"
else
    echo -e "${RED}❌${NC} EduVerify wrong API prefix (should be /api/eduverify)"
    ((ERRORS++))
fi

if grep -q 'prefix="/api/medcare"' microservices/medcare-ai/main.py; then
    echo -e "${GREEN}✅${NC} MedCare correct API prefix (/api/medcare)"
else
    echo -e "${RED}❌${NC} MedCare wrong API prefix (should be /api/medcare)"
    ((ERRORS++))
fi

echo ""

# =============================================
# 6. CHECK KUBERNETES MANIFESTS
# =============================================
echo -e "${BLUE}[6/8] Checking Kubernetes Manifests${NC}"
echo ""

check_file "k8s/00-namespace.yaml" "Namespace manifest"
check_file "k8s/01-configmap-secrets.yaml" "ConfigMap & Secrets"
check_file "k8s/02-ia2good-api-deployment.yaml" "Guardian deployment"
check_file "k8s/03-eduverify-api-deployment.yaml" "EduVerify deployment"
check_file "k8s/04-medcare-api-deployment.yaml" "MedCare deployment"
check_file "k8s/05-ingress-multi-domains.yaml" "Ingress manifest"
check_file "k8s/06-frontend-deployment.yaml" "Frontend deployment"

# Check port consistency
check_port "k8s/02-ia2good-api-deployment.yaml" "8001" "Guardian K8s port"
check_port "k8s/03-eduverify-api-deployment.yaml" "8002" "EduVerify K8s port"
check_port "k8s/04-medcare-api-deployment.yaml" "8003" "MedCare K8s port"

# Check ingress paths
if grep -q "/api/guardian" k8s/05-ingress-multi-domains.yaml; then
    echo -e "${GREEN}✅${NC} Ingress Guardian path configured"
else
    echo -e "${RED}❌${NC} Ingress Guardian path missing"
    ((ERRORS++))
fi

if grep -q "/api/eduverify" k8s/05-ingress-multi-domains.yaml; then
    echo -e "${GREEN}✅${NC} Ingress EduVerify path configured"
else
    echo -e "${RED}❌${NC} Ingress EduVerify path missing"
    ((ERRORS++))
fi

if grep -q "/api/medcare" k8s/05-ingress-multi-domains.yaml; then
    echo -e "${GREEN}✅${NC} Ingress MedCare path configured"
else
    echo -e "${RED}❌${NC} Ingress MedCare path missing"
    ((ERRORS++))
fi

echo ""

# =============================================
# 7. CHECK SCRIPTS
# =============================================
echo -e "${BLUE}[7/8] Checking Deployment Scripts${NC}"
echo ""

check_file "build-and-push.sh" "Build & Push script"
check_file "deploy-k8s.sh" "Deployment script"
check_file "scripts/init-database.sh" "Database init script"

# Check if scripts are executable
if [ -x "build-and-push.sh" ]; then
    echo -e "${GREEN}✅${NC} build-and-push.sh is executable"
else
    echo -e "${YELLOW}⚠️${NC}  build-and-push.sh is not executable (run: chmod +x build-and-push.sh)"
    ((WARNINGS++))
fi

if [ -x "deploy-k8s.sh" ]; then
    echo -e "${GREEN}✅${NC} deploy-k8s.sh is executable"
else
    echo -e "${YELLOW}⚠️${NC}  deploy-k8s.sh is not executable (run: chmod +x deploy-k8s.sh)"
    ((WARNINGS++))
fi

if [ -x "scripts/init-database.sh" ]; then
    echo -e "${GREEN}✅${NC} init-database.sh is executable"
else
    echo -e "${YELLOW}⚠️${NC}  init-database.sh is not executable (run: chmod +x scripts/init-database.sh)"
    ((WARNINGS++))
fi

echo ""

# =============================================
# 8. CHECK DOCUMENTATION
# =============================================
echo -e "${BLUE}[8/8] Checking Documentation${NC}"
echo ""

check_file "README.md" "README documentation"
check_file "DEPLOIEMENT_COMPLET.md" "Deployment guide"
check_file "INTEGRATION_STATUS.md" "Integration status"

echo ""

# =============================================
# SUMMARY
# =============================================
echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Verification Summary${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

if [ $ERRORS -eq 0 ]; then
    echo -e "${GREEN}✅ ALL CHECKS PASSED!${NC}"
    echo ""
    echo -e "${YELLOW}Errors:${NC} ${ERRORS}"
    echo -e "${YELLOW}Warnings:${NC} ${WARNINGS}"
    echo ""
    echo -e "${GREEN}🚀 Ready for deployment!${NC}"
    echo ""
    echo -e "${YELLOW}Next steps:${NC}"
    echo "  1. Configure secrets: vim k8s/01-configmap-secrets.yaml"
    echo "  2. Initialize database: ./scripts/init-database.sh"
    echo "  3. Build images: ./build-and-push.sh"
    echo "  4. Deploy: ./deploy-k8s.sh"
    echo ""
    exit 0
else
    echo -e "${RED}❌ VERIFICATION FAILED${NC}"
    echo ""
    echo -e "${YELLOW}Errors:${NC} ${ERRORS}"
    echo -e "${YELLOW}Warnings:${NC} ${WARNINGS}"
    echo ""
    echo -e "${RED}Please fix the errors before deployment.${NC}"
    echo ""
    exit 1
fi
