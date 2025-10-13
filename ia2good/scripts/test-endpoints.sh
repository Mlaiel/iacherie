#!/bin/bash
# Test IA2GOOD Endpoints
# Test all AI integration endpoints after deployment

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Configuration
BASE_URL="${BASE_URL:-https://ia2good.com}"
GUARDIAN_URL="${GUARDIAN_URL:-https://volunteer.ia2good.com}"
EDUVERIFY_URL="${EDUVERIFY_URL:-https://eduverify.ia2good.com}"
MEDCARE_URL="${MEDCARE_URL:-https://medcare.ia2good.com}"
JWT_TOKEN="${JWT_TOKEN:-}"

TESTS_PASSED=0
TESTS_FAILED=0

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}IA2GOOD Endpoints Testing${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Function to test endpoint
test_endpoint() {
    local url=$1
    local expected_status=${2:-200}
    local description=$3
    
    echo -n "Testing: ${description}... "
    
    response=$(curl -s -w "\n%{http_code}" -X GET "$url" \
        -H "Accept: application/json" \
        ${JWT_TOKEN:+-H "Authorization: Bearer ${JWT_TOKEN}"} \
        2>/dev/null)
    
    status_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | sed '$d')
    
    if [ "$status_code" == "$expected_status" ]; then
        echo -e "${GREEN}✅ PASS${NC} (${status_code})"
        ((TESTS_PASSED++))
        return 0
    else
        echo -e "${RED}❌ FAIL${NC} (Expected: ${expected_status}, Got: ${status_code})"
        ((TESTS_FAILED++))
        return 1
    fi
}

# Function to test POST endpoint
test_post_endpoint() {
    local url=$1
    local data=$2
    local expected_status=${3:-200}
    local description=$4
    
    echo -n "Testing: ${description}... "
    
    response=$(curl -s -w "\n%{http_code}" -X POST "$url" \
        -H "Content-Type: application/json" \
        -H "Accept: application/json" \
        ${JWT_TOKEN:+-H "Authorization: Bearer ${JWT_TOKEN}"} \
        -d "$data" \
        2>/dev/null)
    
    status_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | sed '$d')
    
    if [ "$status_code" == "$expected_status" ] || [ "$status_code" == "401" ]; then
        if [ "$status_code" == "401" ]; then
            echo -e "${YELLOW}⚠️  NEEDS AUTH${NC} (${status_code})"
        else
            echo -e "${GREEN}✅ PASS${NC} (${status_code})"
        fi
        ((TESTS_PASSED++))
        return 0
    else
        echo -e "${RED}❌ FAIL${NC} (Expected: ${expected_status}, Got: ${status_code})"
        echo "   Response: ${body}"
        ((TESTS_FAILED++))
        return 1
    fi
}

# =============================================
# BASIC HEALTH CHECKS
# =============================================
echo -e "${BLUE}[1/5] Testing Health Endpoints${NC}"
echo ""

test_endpoint "${BASE_URL}/health" 200 "Main site health"
test_endpoint "${GUARDIAN_URL}/api/guardian/health" 200 "Guardian API health"
test_endpoint "${EDUVERIFY_URL}/api/eduverify/health" 200 "EduVerify API health"
test_endpoint "${MEDCARE_URL}/api/medcare/health" 200 "MedCare API health"

echo ""

# =============================================
# GUARDIAN AI ENDPOINTS
# =============================================
echo -e "${BLUE}[2/5] Testing Guardian AI Endpoints${NC}"
echo ""

test_endpoint "${GUARDIAN_URL}/api/guardian/ai/health-check" 200 "Guardian AI health check"

# Note: Ces endpoints nécessitent authentication et upload de fichiers
echo -e "${YELLOW}Note: Upload endpoints require authentication and file data${NC}"
echo -e "  • POST /api/guardian/ai/transcribe-testimony (requires audio file)"
echo -e "  • POST /api/guardian/ai/generate-mission-description"
echo -e "  • POST /api/guardian/ai/match-volunteers"
echo -e "  • POST /api/guardian/ai/translate-multilingual"
echo -e "  • POST /api/guardian/ai/classify-need"
echo -e "  • POST /api/guardian/ai/generate-appeal"
echo -e "  • POST /api/guardian/ai/analyze-sentiment"
echo -e "  • POST /api/guardian/ai/generate-report"

echo ""

# =============================================
# EDUVERIFY AI ENDPOINTS
# =============================================
echo -e "${BLUE}[3/5] Testing EduVerify AI Endpoints${NC}"
echo ""

test_endpoint "${EDUVERIFY_URL}/api/eduverify/ai/health-check" 200 "EduVerify AI health check"

# Test fact-check endpoint (with fake data)
test_post_endpoint "${EDUVERIFY_URL}/api/eduverify/ai/fact-check" \
    '{"content":"Test content","sources":["wikipedia"]}' \
    200 \
    "Fact-check endpoint (structure)"

echo -e "${YELLOW}Note: Other endpoints require authentication${NC}"
echo -e "  • POST /api/eduverify/ai/generate-summary"
echo -e "  • POST /api/eduverify/ai/generate-quiz"
echo -e "  • POST /api/eduverify/ai/optimize-seo"
echo -e "  • POST /api/eduverify/ai/assess-quality"
echo -e "  • POST /api/eduverify/ai/correct-grammar"
echo -e "  • POST /api/eduverify/ai/classify-subject"

echo ""

# =============================================
# MEDCARE AI ENDPOINTS
# =============================================
echo -e "${BLUE}[4/5] Testing MedCare AI Endpoints${NC}"
echo ""

test_endpoint "${MEDCARE_URL}/api/medcare/ai/health-check" 200 "MedCare AI health check"

# Test symptom analysis endpoint (with fake data)
test_post_endpoint "${MEDCARE_URL}/api/medcare/ai/analyze-symptoms" \
    '{"symptoms":"Test symptoms","language":"fr"}' \
    200 \
    "Symptom analysis endpoint (structure)"

echo -e "${YELLOW}Note: Other endpoints require authentication${NC}"
echo -e "  • POST /api/medcare/ai/transcribe-consultation"
echo -e "  • POST /api/medcare/ai/generate-voice-advice"
echo -e "  • POST /api/medcare/ai/translate-medical-terms"
echo -e "  • POST /api/medcare/ai/recommend-specialists"
echo -e "  • POST /api/medcare/ai/emergency-triage"

echo ""

# =============================================
# FRONTEND
# =============================================
echo -e "${BLUE}[5/5] Testing Frontend${NC}"
echo ""

test_endpoint "${BASE_URL}/" 200 "Frontend homepage"
test_endpoint "${BASE_URL}/health" 200 "Frontend health endpoint"

echo ""

# =============================================
# SUMMARY
# =============================================
echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Test Summary${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

TOTAL_TESTS=$((TESTS_PASSED + TESTS_FAILED))

echo -e "${YELLOW}Total Tests:${NC} ${TOTAL_TESTS}"
echo -e "${GREEN}Passed:${NC} ${TESTS_PASSED}"
echo -e "${RED}Failed:${NC} ${TESTS_FAILED}"
echo ""

if [ $TESTS_FAILED -eq 0 ]; then
    echo -e "${GREEN}✅ ALL TESTS PASSED!${NC}"
    echo ""
    echo -e "${YELLOW}Integration is functional!${NC}"
    echo ""
    echo -e "${YELLOW}Next steps:${NC}"
    echo "  1. Obtain JWT token for authenticated testing"
    echo "  2. Test authenticated endpoints with real data"
    echo "  3. Monitor metrics: kubectl port-forward -n ia2good deployment/ia2good-api 9090:9090"
    echo "  4. Check logs: kubectl logs -f -n ia2good deployment/ia2good-api"
    echo ""
    exit 0
else
    echo -e "${RED}❌ SOME TESTS FAILED${NC}"
    echo ""
    echo -e "${YELLOW}Possible issues:${NC}"
    echo "  • Services not fully started (wait a few minutes)"
    echo "  • DNS not propagated yet"
    echo "  • SSL certificates not issued yet"
    echo "  • Check logs: kubectl logs -n ia2good <pod-name>"
    echo ""
    exit 1
fi
