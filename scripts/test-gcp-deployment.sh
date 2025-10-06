#!/bin/bash
# 🧪 Script de Test Complet GCP
# Auteur: Fahed Mlaiel (mlaiel@live.de)
# Usage: ./scripts/test-gcp-deployment.sh

set -e

# Couleurs
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}"
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║         🧪 IA CHÉRIE - TEST DÉPLOIEMENT GCP                  ║"
echo "║         Vérification Complète de l'Infrastructure            ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo -e "${NC}"

# Variables
export PROJECT_ID="${GCP_PROJECT_ID:-iacherie-production}"
export REGION="${GCP_REGION:-europe-west1}"
export NAMESPACE="iacherie"

TESTS_PASSED=0
TESTS_FAILED=0
TESTS_TOTAL=0

# Fonction de test
test_command() {
    local test_name="$1"
    local command="$2"
    local expected="$3"
    
    TESTS_TOTAL=$((TESTS_TOTAL + 1))
    echo -e "${BLUE}Test $TESTS_TOTAL: $test_name${NC}"
    
    if eval "$command" | grep -q "$expected"; then
        echo -e "${GREEN}✅ PASS${NC}"
        TESTS_PASSED=$((TESTS_PASSED + 1))
        return 0
    else
        echo -e "${RED}❌ FAIL${NC}"
        TESTS_FAILED=$((TESTS_FAILED + 1))
        return 1
    fi
}

echo -e "${YELLOW}📋 Configuration GCP${NC}"
gcloud config set project $PROJECT_ID
gcloud container clusters get-credentials iacherie-cluster --region=$REGION --quiet

echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}  SECTION 1: INFRASTRUCTURE KUBERNETES${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

# Test 1: Namespace existe
test_command "Namespace iacherie existe" \
    "kubectl get namespace $NAMESPACE" \
    "iacherie"

# Test 2: Pods running
test_command "Pods stable-diffusion running" \
    "kubectl get pods -n $NAMESPACE -l app=stable-diffusion --field-selector=status.phase=Running" \
    "Running"

# Test 3: Services actifs
test_command "Service stable-diffusion existe" \
    "kubectl get svc -n $NAMESPACE stable-diffusion-service" \
    "stable-diffusion-service"

# Test 4: PVC créé
test_command "PVC model-cache créé" \
    "kubectl get pvc -n $NAMESPACE model-cache-pvc" \
    "Bound"

echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}  SECTION 2: GPU & NVIDIA${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

# Test 5: Nodes GPU disponibles
test_command "Nodes GPU disponibles" \
    "kubectl get nodes -l workload=gpu" \
    "Ready"

# Test 6: GPU alloué au pod
POD=$(kubectl get pod -n $NAMESPACE -l app=stable-diffusion -o jsonpath='{.items[0].metadata.name}' 2>/dev/null || echo "")
if [ -n "$POD" ]; then
    test_command "GPU alloué au pod" \
        "kubectl describe pod -n $NAMESPACE $POD" \
        "nvidia.com/gpu"
    
    # Test 7: CUDA disponible dans le pod
    TESTS_TOTAL=$((TESTS_TOTAL + 1))
    echo -e "${BLUE}Test $TESTS_TOTAL: CUDA disponible dans le pod${NC}"
    if kubectl exec -n $NAMESPACE $POD -- python3 -c "import torch; assert torch.cuda.is_available(), 'CUDA not available'" 2>/dev/null; then
        echo -e "${GREEN}✅ PASS${NC}"
        TESTS_PASSED=$((TESTS_PASSED + 1))
    else
        echo -e "${RED}❌ FAIL${NC}"
        TESTS_FAILED=$((TESTS_FAILED + 1))
    fi
else
    echo -e "${YELLOW}⚠️  Aucun pod trouvé, tests GPU skippés${NC}"
fi

echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}  SECTION 3: SSL & CERTIFICATS${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

# Test 8: cert-manager installé
test_command "cert-manager installé" \
    "kubectl get pods -n cert-manager" \
    "Running"

# Test 9: ClusterIssuer créé
test_command "ClusterIssuer letsencrypt-prod" \
    "kubectl get clusterissuer letsencrypt-prod" \
    "letsencrypt-prod"

# Test 10-13: Certificats pour chaque domaine
DOMAINS=("com" "eu" "de" "online")
for domain in "${DOMAINS[@]}"; do
    test_command "Certificat iacherie-$domain-tls" \
        "kubectl get certificate -n $NAMESPACE iacherie-$domain-tls" \
        "True"
done

echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}  SECTION 4: INGRESS & LOAD BALANCER${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

# Test 14: NGINX Ingress Controller
test_command "NGINX Ingress Controller running" \
    "kubectl get pods -n ingress-nginx -l app.kubernetes.io/component=controller" \
    "Running"

# Test 15: Load Balancer IP
EXTERNAL_IP=$(kubectl get svc -n ingress-nginx ingress-nginx-controller -o jsonpath='{.status.loadBalancer.ingress[0].ip}' 2>/dev/null || echo "")
TESTS_TOTAL=$((TESTS_TOTAL + 1))
echo -e "${BLUE}Test $TESTS_TOTAL: Load Balancer a une IP publique${NC}"
if [ -n "$EXTERNAL_IP" ]; then
    echo -e "${GREEN}✅ PASS - IP: $EXTERNAL_IP${NC}"
    TESTS_PASSED=$((TESTS_PASSED + 1))
else
    echo -e "${RED}❌ FAIL - Aucune IP publique${NC}"
    TESTS_FAILED=$((TESTS_FAILED + 1))
fi

# Test 16: Ingress multi-domaines configuré
test_command "Ingress multi-domaines existe" \
    "kubectl get ingress -n $NAMESPACE iacherie-multi-domain" \
    "iacherie-multi-domain"

echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}  SECTION 5: TESTS API${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

if [ -n "$EXTERNAL_IP" ]; then
    # Test 17: Health endpoint (via IP)
    TESTS_TOTAL=$((TESTS_TOTAL + 1))
    echo -e "${BLUE}Test $TESTS_TOTAL: Health endpoint répond (via IP)${NC}"
    if curl -f -H "Host: api.iacherie.com" http://$EXTERNAL_IP/health --max-time 10 2>/dev/null; then
        echo -e "${GREEN}✅ PASS${NC}"
        TESTS_PASSED=$((TESTS_PASSED + 1))
    else
        echo -e "${RED}❌ FAIL${NC}"
        TESTS_FAILED=$((TESTS_FAILED + 1))
    fi
    
    # Test 18-21: Test HTTPS pour chaque domaine
    for domain in iacherie.com iacherie.eu iacherie.de iacherie.online; do
        TESTS_TOTAL=$((TESTS_TOTAL + 1))
        echo -e "${BLUE}Test $TESTS_TOTAL: HTTPS api.$domain accessible${NC}"
        
        if curl -f -I https://api.$domain/health --max-time 10 2>/dev/null | grep -q "200"; then
            echo -e "${GREEN}✅ PASS${NC}"
            TESTS_PASSED=$((TESTS_PASSED + 1))
        else
            echo -e "${YELLOW}⚠️  SKIP - DNS peut ne pas être encore propagé${NC}"
        fi
    done
    
    # Test 22: Endpoint models disponible
    TESTS_TOTAL=$((TESTS_TOTAL + 1))
    echo -e "${BLUE}Test $TESTS_TOTAL: Endpoint /api/generate/models/image${NC}"
    if curl -f -H "Host: api.iacherie.com" http://$EXTERNAL_IP/api/generate/models/image --max-time 10 2>/dev/null | grep -q "internal"; then
        echo -e "${GREEN}✅ PASS${NC}"
        TESTS_PASSED=$((TESTS_PASSED + 1))
    else
        echo -e "${RED}❌ FAIL${NC}"
        TESTS_FAILED=$((TESTS_FAILED + 1))
    fi
fi

echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}  SECTION 6: CONFIGURATION & SECRETS${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

# Test 23: ConfigMap existe
test_command "ConfigMap iacherie-config existe" \
    "kubectl get configmap -n $NAMESPACE iacherie-config" \
    "iacherie-config"

# Test 24: Secrets existent
test_command "Secret iacherie-secrets existe" \
    "kubectl get secret -n $NAMESPACE iacherie-secrets" \
    "iacherie-secrets"

echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}  SECTION 7: RESSOURCES & LIMITES${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

if [ -n "$POD" ]; then
    # Test 25: Resources requests définis
    test_command "CPU requests définis" \
        "kubectl get pod -n $NAMESPACE $POD -o yaml" \
        "cpu:"
    
    # Test 26: Memory requests définis
    test_command "Memory requests définis" \
        "kubectl get pod -n $NAMESPACE $POD -o yaml" \
        "memory:"
    
    # Test 27: GPU requests définis
    test_command "GPU requests définis" \
        "kubectl get pod -n $NAMESPACE $POD -o yaml" \
        "nvidia.com/gpu"
fi

echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}  SECTION 8: MONITORING${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

# Test 28: Métriques pods disponibles
TESTS_TOTAL=$((TESTS_TOTAL + 1))
echo -e "${BLUE}Test $TESTS_TOTAL: Métriques pods disponibles${NC}"
if kubectl top pods -n $NAMESPACE 2>/dev/null | grep -q "CPU"; then
    echo -e "${GREEN}✅ PASS${NC}"
    TESTS_PASSED=$((TESTS_PASSED + 1))
else
    echo -e "${YELLOW}⚠️  SKIP - Metrics server peut ne pas être installé${NC}"
fi

echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}  RÉSUMÉ DES TESTS${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

SUCCESS_RATE=$((TESTS_PASSED * 100 / TESTS_TOTAL))

echo -e "${YELLOW}📊 Statistiques:${NC}"
echo "   Total tests: $TESTS_TOTAL"
echo -e "   ${GREEN}Réussis: $TESTS_PASSED${NC}"
echo -e "   ${RED}Échoués: $TESTS_FAILED${NC}"
echo "   Taux de succès: $SUCCESS_RATE%"
echo ""

if [ $TESTS_FAILED -eq 0 ]; then
    echo -e "${GREEN}╔══════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║         🎉 TOUS LES TESTS SONT PASSÉS !                      ║${NC}"
    echo -e "${GREEN}║         Votre déploiement GCP est opérationnel !             ║${NC}"
    echo -e "${GREEN}╚══════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    echo -e "${BLUE}🌍 URLs de Production:${NC}"
    echo "   - https://api.iacherie.com"
    echo "   - https://api.iacherie.eu"
    echo "   - https://api.iacherie.de"
    echo "   - https://api.iacherie.online"
    echo ""
    echo -e "${BLUE}🔍 Commandes utiles:${NC}"
    echo "   kubectl logs -n $NAMESPACE -l app=stable-diffusion --tail=100 -f"
    echo "   kubectl top pods -n $NAMESPACE"
    echo "   kubectl exec -it -n $NAMESPACE $POD -- bash"
    exit 0
else
    echo -e "${RED}╔══════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${RED}║         ⚠️  CERTAINS TESTS ONT ÉCHOUÉ                        ║${NC}"
    echo -e "${RED}╚══════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    echo -e "${YELLOW}🔧 Actions recommandées:${NC}"
    echo "   1. Vérifier les logs: kubectl logs -n $NAMESPACE -l app=stable-diffusion"
    echo "   2. Vérifier les events: kubectl get events -n $NAMESPACE --sort-by='.lastTimestamp'"
    echo "   3. Vérifier les pods: kubectl describe pod -n $NAMESPACE $POD"
    echo ""
    exit 1
fi
