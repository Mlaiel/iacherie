#!/bin/bash
################################################################################
# Tests Complets - Validation Implémentations Réelles
# Teste tous les endpoints avec vraies implémentations IA
################################################################################

# Couleurs
GREEN='\033[0;32m'
RED='\033[0;31m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Compteurs
PASSED=0
FAILED=0

# Fonction de test
test_endpoint() {
    local name=$1
    local url=$2
    local data=$3
    local expected_field=$4
    
    echo -n "🧪 Test: $name... "
    
    response=$(curl -s -X POST "$url" \
        -H "Content-Type: application/json" \
        -d "$data")
    
    if echo "$response" | jq -e ".$expected_field" > /dev/null 2>&1; then
        echo -e "${GREEN}✅ PASSÉ${NC}"
        ((PASSED++))
        
        # Afficher détails clés
        echo "$response" | jq -c "{provider: .provider, cost: .cost, success}" | head -1
    else
        echo -e "${RED}❌ ÉCHOUÉ${NC}"
        ((FAILED++))
        echo "Response: $response" | head -c 200
    fi
    echo ""
}

echo -e "${BLUE}╔════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║  TESTS COMPLETS - IMPLÉMENTATIONS RÉELLES IA         ║${NC}"
echo -e "${BLUE}╔════════════════════════════════════════════════════════╗${NC}"
echo ""

# ============================================================================
# SECTION 1: IACHERIE CORE
# ============================================================================

echo -e "${YELLOW}━━━ SECTION 1: IACherie Core (Port 8000) ━━━${NC}"
echo ""

test_endpoint \
    "Génération texte grippe (internal-gpt-xl)" \
    "http://localhost:8000/api/generate/text" \
    '{"prompt": "Explique la grippe en détail", "model": "internal-gpt-xl", "max_tokens": 300}' \
    "data.provider"

test_endpoint \
    "Quiz médical diabète" \
    "http://localhost:8000/api/ai-agents/generate-quiz" \
    '{"content": "Le diabète est une maladie chronique", "num_questions": 3}' \
    "questions"

test_endpoint \
    "Résumé bullet_points" \
    "http://localhost:8000/api/ai-agents/summarize" \
    '{"content": "La photosynthèse est un processus biologique essentiel. Elle convertit la lumière solaire en énergie chimique.", "style": "bullet_points"}' \
    "summary"

test_endpoint \
    "Fact-check éducatif" \
    "http://localhost:8000/api/ai-agents/fact-check" \
    '{"claim": "La Terre tourne autour du Soleil", "domain": "education"}' \
    "verified"

test_endpoint \
    "Analyse symptômes médicaux" \
    "http://localhost:8000/api/ai-agents/medical/symptom-analysis" \
    '{"symptoms": ["fièvre", "toux", "fatigue"], "severity": 7}' \
    "urgency"

test_endpoint \
    "Traduction médicale FR→EN" \
    "http://localhost:8000/api/languages/translate" \
    '{"text": "fièvre et toux", "source_language": "fr", "target_language": "en", "domain": "medical"}' \
    "translated_text"

# ============================================================================
# SECTION 2: EDUVERIFY
# ============================================================================

echo ""
echo -e "${YELLOW}━━━ SECTION 2: EduVerify (Port 8002) ━━━${NC}"
echo ""

test_endpoint \
    "EduVerify - Fact-check contenu" \
    "http://localhost:8002/api/eduverify/ai/fact-check" \
    '{"content": "La Terre est ronde et orbite autour du Soleil"}' \
    "verified"

test_endpoint \
    "EduVerify - Résumé éducatif" \
    "http://localhost:8002/api/eduverify/ai/generate-summary" \
    '{"content": "La photosynthèse transforme lumière en énergie. Processus vital pour plantes.", "style": "concise"}' \
    "summary"

test_endpoint \
    "EduVerify - Quiz photosynthèse" \
    "http://localhost:8002/api/eduverify/ai/generate-quiz" \
    '{"content": "La photosynthèse utilise CO2 et eau pour produire glucose et oxygène", "num_questions": 2}' \
    "quiz.questions"

# ============================================================================
# SECTION 3: MEDCARE AI
# ============================================================================

echo ""
echo -e "${YELLOW}━━━ SECTION 3: MedCare AI (Port 8003) ━━━${NC}"
echo ""

test_endpoint \
    "MedCare - Analyse symptômes légers" \
    "http://localhost:8003/api/medcare/ai/analyze-symptoms" \
    '{"symptoms": "mal de gorge, léger mal de tête", "severity": 3}' \
    "urgency"

test_endpoint \
    "MedCare - Analyse symptômes urgents" \
    "http://localhost:8003/api/medcare/ai/analyze-symptoms" \
    '{"symptoms": "fièvre élevée, difficultés respiratoires", "severity": 8}' \
    "red_flags"

test_endpoint \
    "MedCare - Triage urgence cardiaque" \
    "http://localhost:8003/api/medcare/ai/emergency-triage" \
    '{"symptoms": "douleur thoracique intense, essoufflement"}' \
    "priority"

test_endpoint \
    "MedCare - Traduction termes médicaux" \
    "http://localhost:8003/api/medcare/ai/translate-medical-terms" \
    '{"terms": ["fièvre", "mal de gorge", "toux"], "source_language": "fr", "target_language": "en"}' \
    "translations"

# ============================================================================
# RÉSULTATS
# ============================================================================

echo ""
echo -e "${BLUE}╔════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║  RÉSULTATS FINAUX                                     ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════╝${NC}"
echo ""

TOTAL=$((PASSED + FAILED))
SUCCESS_RATE=$((PASSED * 100 / TOTAL))

if [ $SUCCESS_RATE -ge 90 ]; then
    COLOR=$GREEN
    STATUS="✅ EXCELLENT"
elif [ $SUCCESS_RATE -ge 70 ]; then
    COLOR=$YELLOW
    STATUS="⚠️  ACCEPTABLE"
else
    COLOR=$RED
    STATUS="❌ CRITIQUE"
fi

echo -e "Tests passés:   ${GREEN}$PASSED${NC}"
echo -e "Tests échoués:  ${RED}$FAILED${NC}"
echo -e "Total:          $TOTAL"
echo -e "Taux succès:    ${COLOR}$SUCCESS_RATE%${NC}"
echo -e "Status:         ${COLOR}$STATUS${NC}"
echo ""

if [ $SUCCESS_RATE -eq 100 ]; then
    echo -e "${GREEN}🎉 FÉLICITATIONS! Toutes les implémentations sont fonctionnelles!${NC}"
    echo -e "${GREEN}✨ Système 100% opérationnel avec vraies IA (0€)${NC}"
elif [ $SUCCESS_RATE -ge 90 ]; then
    echo -e "${GREEN}✅ Excellent! Le système est production-ready.${NC}"
elif [ $SUCCESS_RATE -ge 70 ]; then
    echo -e "${YELLOW}⚠️  Système fonctionnel mais nécessite optimisations.${NC}"
else
    echo -e "${RED}❌ Attention: Plusieurs composants nécessitent corrections.${NC}"
fi

echo ""
echo "📝 Logs disponibles:"
echo "   • IACherie:  tail -f /tmp/iacherie_api.log"
echo "   • EduVerify: tail -f /tmp/eduverify_api.log"
echo "   • MedCare:   tail -f /tmp/medcare_api.log"
echo ""

exit $FAILED
