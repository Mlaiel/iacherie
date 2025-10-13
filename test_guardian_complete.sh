#!/bin/bash

###############################################################################
# GUARDIAN VOLUNTEER PLATFORM - COMPLETE TEST SUITE
# Tests all Guardian endpoints and Guardian AI integration
###############################################################################

set -e

echo "========================================================================="
echo "🌍 GUARDIAN VOLUNTEER PLATFORM - COMPLETE TEST SUITE"
echo "========================================================================="
echo ""

GUARDIAN_URL="http://localhost:8001"
IACHERIE_URL="http://localhost:8000"

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test counters
TOTAL_TESTS=0
PASSED_TESTS=0
FAILED_TESTS=0

# Test function
test_endpoint() {
    TOTAL_TESTS=$((TOTAL_TESTS + 1))
    TEST_NAME="$1"
    METHOD="$2"
    URL="$3"
    DATA="$4"
    EXPECTED_FIELD="$5"
    
    echo -e "${YELLOW}Testing: $TEST_NAME${NC}"
    
    if [ "$METHOD" = "GET" ]; then
        RESPONSE=$(curl -s "$URL")
    else
        RESPONSE=$(curl -s -X "$METHOD" "$URL" -H "Content-Type: application/json" -d "$DATA")
    fi
    
    if echo "$RESPONSE" | jq -e ".$EXPECTED_FIELD" > /dev/null 2>&1; then
        echo -e "${GREEN}✅ PASS: $TEST_NAME${NC}"
        PASSED_TESTS=$((PASSED_TESTS + 1))
        echo "$RESPONSE" | jq .
    else
        echo -e "${RED}❌ FAIL: $TEST_NAME${NC}"
        FAILED_TESTS=$((FAILED_TESTS + 1))
        echo "Response: $RESPONSE"
    fi
    echo ""
}

echo "========================================================================="
echo "1️⃣ HEALTH CHECKS"
echo "========================================================================="

test_endpoint "Guardian Health Check" "GET" "$GUARDIAN_URL/health" "" "status"
test_endpoint "IACherie Health Check" "GET" "$IACHERIE_URL/health" "" "status"

echo "========================================================================="
echo "2️⃣ MISSION MANAGEMENT"
echo "========================================================================="

# Create Mission 1 - Environment
test_endpoint "Create Environment Mission" "POST" "$GUARDIAN_URL/api/guardian/missions" \
'{
    "title": "Beach Cleanup Santa Monica",
    "description": "Clean up the beach to protect marine life",
    "category": "environment",
    "location": "Santa Monica Beach, CA",
    "volunteers_needed": 15
}' "id"

# Create Mission 2 - Animal
test_endpoint "Create Animal Mission" "POST" "$GUARDIAN_URL/api/guardian/missions" \
'{
    "title": "Animal Shelter Support",
    "description": "Help care for rescue animals",
    "category": "animal",
    "location": "LA Animal Shelter",
    "volunteers_needed": 8
}' "id"

# Create Mission 3 - Homeless
test_endpoint "Create Homeless Mission" "POST" "$GUARDIAN_URL/api/guardian/missions" \
'{
    "title": "Winter Meal Distribution",
    "description": "Distribute hot meals to homeless individuals",
    "category": "homeless",
    "location": "Downtown LA",
    "volunteers_needed": 12
}' "id"

# List all missions
test_endpoint "List All Missions" "GET" "$GUARDIAN_URL/api/guardian/missions" "" "0"

# Get specific mission
test_endpoint "Get Mission Details" "GET" "$GUARDIAN_URL/api/guardian/missions/1" "" "title"

echo "========================================================================="
echo "3️⃣ VOLUNTEER REGISTRATION"
echo "========================================================================="

# Register Volunteer 1
test_endpoint "Register Volunteer 1" "POST" "$GUARDIAN_URL/api/guardian/volunteers" \
'{
    "name": "Alice Johnson",
    "email": "alice@example.com",
    "phone": "+1-555-0101",
    "skills": ["first aid", "environmental science", "organization"]
}' "id"

# Register Volunteer 2
test_endpoint "Register Volunteer 2" "POST" "$GUARDIAN_URL/api/guardian/volunteers" \
'{
    "name": "Bob Smith",
    "email": "bob@example.com",
    "phone": "+1-555-0102",
    "skills": ["animal care", "veterinary assistance"]
}' "id"

# Register Volunteer 3
test_endpoint "Register Volunteer 3" "POST" "$GUARDIAN_URL/api/guardian/volunteers" \
'{
    "name": "Carol Martinez",
    "email": "carol@example.com",
    "phone": "+1-555-0103",
    "skills": ["cooking", "social work", "Spanish language"]
}' "id"

# List all volunteers
test_endpoint "List All Volunteers" "GET" "$GUARDIAN_URL/api/guardian/volunteers" "" "0"

# Get specific volunteer
test_endpoint "Get Volunteer Details" "GET" "$GUARDIAN_URL/api/guardian/volunteers/1" "" "name"

echo "========================================================================="
echo "4️⃣ GUARDIAN AI ASSISTANCE"
echo "========================================================================="

# AI Assistance - Environment
test_endpoint "AI: Beach Cleanup Guidance" "POST" "$GUARDIAN_URL/api/guardian/ai" \
'{
    "query": "How do I organize a beach cleanup mission with 15 volunteers?",
    "context": "We have 2km of beach to clean",
    "category": "environment"
}' "result"

# AI Assistance - Animal
test_endpoint "AI: Animal Shelter Support" "POST" "$GUARDIAN_URL/api/guardian/ai" \
'{
    "query": "What are the best ways to support an animal shelter?",
    "context": "We want to volunteer regularly",
    "category": "animal"
}' "result"

# AI Assistance - Homeless
test_endpoint "AI: Meal Distribution Planning" "POST" "$GUARDIAN_URL/api/guardian/ai" \
'{
    "query": "How should we distribute meals to homeless people?",
    "context": "We have 50 meals and 3 hours",
    "category": "homeless"
}' "result"

# AI Assistance - Humanitarian
test_endpoint "AI: Disaster Relief" "POST" "$GUARDIAN_URL/api/guardian/ai" \
'{
    "query": "What are the first steps in disaster relief?",
    "context": "Natural disaster just occurred",
    "category": "humanitarian"
}' "result"

echo "========================================================================="
echo "📊 TEST SUMMARY"
echo "========================================================================="

echo ""
echo "Total Tests: $TOTAL_TESTS"
echo -e "${GREEN}Passed: $PASSED_TESTS${NC}"
echo -e "${RED}Failed: $FAILED_TESTS${NC}"
echo ""

if [ $FAILED_TESTS -eq 0 ]; then
    echo -e "${GREEN}🎉 ALL TESTS PASSED! Guardian Volunteer Platform is operational!${NC}"
    exit 0
else
    echo -e "${RED}❌ Some tests failed. Please review the output above.${NC}"
    exit 1
fi
