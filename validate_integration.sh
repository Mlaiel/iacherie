#!/bin/bash

echo "================================================================"
echo "🎯 VALIDATION FINALE - INTÉGRATION IACHERIE + IA2GOOD"
echo "================================================================"
echo ""

# Couleurs
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

TOTAL_TESTS=0
PASSED_TESTS=0
FAILED_TESTS=0

# Fonction de test
test_service() {
    local name=$1
    local url=$2
    local expected=$3
    
    TOTAL_TESTS=$((TOTAL_TESTS + 1))
    echo -n "Testing $name... "
    
    response=$(curl -s -w "%{http_code}" -o /tmp/test_response.json "$url" 2>/dev/null)
    http_code="${response: -3}"
    
    if [ "$http_code" = "200" ]; then
        if grep -q "$expected" /tmp/test_response.json 2>/dev/null; then
            echo -e "${GREEN}✅ PASSED${NC}"
            PASSED_TESTS=$((PASSED_TESTS + 1))
            return 0
        else
            echo -e "${RED}❌ FAILED${NC} (unexpected response)"
            FAILED_TESTS=$((FAILED_TESTS + 1))
            return 1
        fi
    else
        echo -e "${RED}❌ FAILED${NC} (HTTP $http_code)"
        FAILED_TESTS=$((FAILED_TESTS + 1))
        return 1
    fi
}

# Tests des services
echo "📊 Testing Services Health..."
echo ""

test_service "IACherie API    (8000)" "http://localhost:8000/health" "healthy"
test_service "Guardian        (8001)" "http://localhost:8001/health" "healthy"
test_service "EduVerify       (8002)" "http://localhost:8002/health" "healthy"
test_service "MedCare         (8003)" "http://localhost:8003/health" "healthy"

echo ""
echo "🗄️  Testing PostgreSQL..."
echo ""

# Test PostgreSQL
TOTAL_TESTS=$((TOTAL_TESTS + 1))
echo -n "Testing PostgreSQL connectivity... "
if docker exec ia2good-postgres psql -U ia2good -d ia2good -c "SELECT 1;" > /dev/null 2>&1; then
    echo -e "${GREEN}✅ PASSED${NC}"
    PASSED_TESTS=$((PASSED_TESTS + 1))
else
    echo -e "${RED}❌ FAILED${NC}"
    FAILED_TESTS=$((FAILED_TESTS + 1))
fi

# Test tables EduVerify
TOTAL_TESTS=$((TOTAL_TESTS + 1))
echo -n "Testing EduVerify tables... "
table_count=$(docker exec ia2good-postgres psql -U ia2good -d ia2good -t -c "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema='public' AND table_name LIKE 'eduverify_%';" 2>/dev/null | tr -d ' ')
if [ "$table_count" -eq "9" ]; then
    echo -e "${GREEN}✅ PASSED${NC} (9 tables)"
    PASSED_TESTS=$((PASSED_TESTS + 1))
else
    echo -e "${RED}❌ FAILED${NC} (found $table_count tables, expected 9)"
    FAILED_TESTS=$((FAILED_TESTS + 1))
fi

# Test tables MedCare
TOTAL_TESTS=$((TOTAL_TESTS + 1))
echo -n "Testing MedCare tables... "
table_count=$(docker exec ia2good-postgres psql -U ia2good -d ia2good -t -c "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema='public' AND table_name LIKE 'medcare_%';" 2>/dev/null | tr -d ' ')
if [ "$table_count" -eq "13" ]; then
    echo -e "${GREEN}✅ PASSED${NC} (13 tables)"
    PASSED_TESTS=$((PASSED_TESTS + 1))
else
    echo -e "${RED}❌ FAILED${NC} (found $table_count tables, expected 13)"
    FAILED_TESTS=$((FAILED_TESTS + 1))
fi

# Test extensions PostgreSQL
TOTAL_TESTS=$((TOTAL_TESTS + 1))
echo -n "Testing PostgreSQL extensions... "
if docker exec ia2good-postgres psql -U ia2good -d ia2good -c "SELECT 1 FROM pg_extension WHERE extname IN ('uuid-ossp', 'pg_trgm');" 2>/dev/null | grep -q "2 rows"; then
    echo -e "${GREEN}✅ PASSED${NC} (uuid-ossp, pg_trgm)"
    PASSED_TESTS=$((PASSED_TESTS + 1))
else
    echo -e "${YELLOW}⚠️  WARNING${NC} (extensions may not be fully loaded)"
    FAILED_TESTS=$((FAILED_TESTS + 1))
fi

echo ""
echo "🔗 Testing AI Integration..."
echo ""

# Test Guardian → IACherie integration
TOTAL_TESTS=$((TOTAL_TESTS + 1))
echo -n "Testing Guardian AI integration... "
if curl -s http://localhost:8001/health | grep -q "iacherie_ai.*healthy"; then
    echo -e "${GREEN}✅ PASSED${NC}"
    PASSED_TESTS=$((PASSED_TESTS + 1))
else
    echo -e "${YELLOW}⚠️  WARNING${NC} (IACherie AI may not be fully connected)"
    FAILED_TESTS=$((FAILED_TESTS + 1))
fi

# Test EduVerify → IACherie integration
TOTAL_TESTS=$((TOTAL_TESTS + 1))
echo -n "Testing EduVerify AI integration... "
if curl -s http://localhost:8002/health | grep -q "iacherie_ai.*connected"; then
    echo -e "${GREEN}✅ PASSED${NC}"
    PASSED_TESTS=$((PASSED_TESTS + 1))
else
    echo -e "${YELLOW}⚠️  WARNING${NC}"
    FAILED_TESTS=$((FAILED_TESTS + 1))
fi

# Test MedCare → IACherie integration
TOTAL_TESTS=$((TOTAL_TESTS + 1))
echo -n "Testing MedCare AI integration... "
if curl -s http://localhost:8003/health | grep -q "iacherie_ai.*ok"; then
    echo -e "${GREEN}✅ PASSED${NC}"
    PASSED_TESTS=$((PASSED_TESTS + 1))
else
    echo -e "${YELLOW}⚠️  WARNING${NC}"
    FAILED_TESTS=$((FAILED_TESTS + 1))
fi

# Résumé
echo ""
echo "================================================================"
echo "📊 RÉSULTATS FINAUX"
echo "================================================================"
echo ""
echo "Total tests:  $TOTAL_TESTS"
echo -e "Passed:       ${GREEN}$PASSED_TESTS${NC}"
if [ $FAILED_TESTS -gt 0 ]; then
    echo -e "Failed:       ${RED}$FAILED_TESTS${NC}"
else
    echo -e "Failed:       ${GREEN}$FAILED_TESTS${NC}"
fi
echo ""

# Calcul pourcentage
SUCCESS_RATE=$(( (PASSED_TESTS * 100) / TOTAL_TESTS ))

if [ $SUCCESS_RATE -eq 100 ]; then
    echo -e "${GREEN}🎉 SUCCESS RATE: 100% - TOUS LES TESTS PASSÉS!${NC}"
    echo ""
    echo "✅ IACherie + IA2GOOD est 100% opérationnel!"
    exit 0
elif [ $SUCCESS_RATE -ge 80 ]; then
    echo -e "${YELLOW}⚠️  SUCCESS RATE: ${SUCCESS_RATE}% - Quelques warnings${NC}"
    echo ""
    echo "✅ Le système est opérationnel mais avec quelques avertissements."
    exit 0
else
    echo -e "${RED}❌ SUCCESS RATE: ${SUCCESS_RATE}% - Des problèmes détectés${NC}"
    echo ""
    echo "❌ Veuillez vérifier les logs pour plus de détails."
    exit 1
fi
