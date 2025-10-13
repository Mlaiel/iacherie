#!/bin/bash

###############################################################################
# GUARDIAN GEO & REAL-TIME MAP - TEST SUITE
# Tests all geographic and real-time tracking features
###############################################################################

set -e

echo "========================================================================="
echo "🗺️ GUARDIAN GEO & REAL-TIME MAP - TEST SUITE"
echo "========================================================================="
echo ""

GUARDIAN_URL="http://localhost:8001"

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
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
echo "1️⃣ SETUP - Create Test Missions and Volunteers"
echo "========================================================================="

# Create Mission 1
curl -s -X POST "$GUARDIAN_URL/api/guardian/missions" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Beach Cleanup Santa Monica",
    "description": "Clean up the beach",
    "category": "environment",
    "location": "Santa Monica Beach",
    "volunteers_needed": 10
  }' > /dev/null

# Create Mission 2
curl -s -X POST "$GUARDIAN_URL/api/guardian/missions" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Animal Shelter Support",
    "description": "Help care for animals",
    "category": "animal",
    "location": "LA Animal Shelter",
    "volunteers_needed": 8
  }' > /dev/null

# Create Mission 3
curl -s -X POST "$GUARDIAN_URL/api/guardian/missions" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Homeless Meal Distribution",
    "description": "Distribute meals",
    "category": "homeless",
    "location": "Downtown LA",
    "volunteers_needed": 12
  }' > /dev/null

echo -e "${GREEN}✅ Created 3 test missions${NC}"
echo ""

# Register Volunteers
curl -s -X POST "$GUARDIAN_URL/api/guardian/volunteers" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Alice Johnson",
    "email": "alice@example.com",
    "skills": ["first aid", "environmental science"]
  }' > /dev/null

curl -s -X POST "$GUARDIAN_URL/api/guardian/volunteers" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Bob Smith",
    "email": "bob@example.com",
    "skills": ["animal care"]
  }' > /dev/null

echo -e "${GREEN}✅ Registered 2 test volunteers${NC}"
echo ""

echo "========================================================================="
echo "2️⃣ MISSION LOCATIONS"
echo "========================================================================="

# Set location for Mission 1 (Santa Monica Beach)
test_endpoint "Set Mission 1 Location (Santa Monica)" "POST" \
  "$GUARDIAN_URL/api/guardian/geo/missions/1/location?category=environment" \
  '{
    "latitude": 34.0195,
    "longitude": -118.4912,
    "address": "Santa Monica Beach, CA"
  }' "success"

# Set location for Mission 2 (LA Animal Shelter)
test_endpoint "Set Mission 2 Location (Animal Shelter)" "POST" \
  "$GUARDIAN_URL/api/guardian/geo/missions/2/location?category=animal" \
  '{
    "latitude": 34.0522,
    "longitude": -118.2437,
    "address": "LA Animal Shelter, Downtown"
  }' "success"

# Set location for Mission 3 (Downtown LA)
test_endpoint "Set Mission 3 Location (Downtown)" "POST" \
  "$GUARDIAN_URL/api/guardian/geo/missions/3/location?category=homeless" \
  '{
    "latitude": 34.0407,
    "longitude": -118.2468,
    "address": "Downtown Los Angeles"
  }' "success"

# Get all mission locations
test_endpoint "Get All Mission Locations" "GET" \
  "$GUARDIAN_URL/api/guardian/geo/missions/locations" "" "missions"

# Get specific mission location
test_endpoint "Get Mission 1 Location" "GET" \
  "$GUARDIAN_URL/api/guardian/geo/missions/1/location" "" "mission"

echo "========================================================================="
echo "3️⃣ VOLUNTEER LOCATIONS (Real-time Tracking)"
echo "========================================================================="

# Update volunteer 1 location
test_endpoint "Update Volunteer 1 Location" "POST" \
  "$GUARDIAN_URL/api/guardian/geo/volunteers/1/location?mission_id=1" \
  '{
    "latitude": 34.0195,
    "longitude": -118.4912,
    "address": "En route to Santa Monica",
    "timestamp": "'$(date -u +"%Y-%m-%dT%H:%M:%S")'"
  }' "success"

# Update volunteer 2 location
test_endpoint "Update Volunteer 2 Location" "POST" \
  "$GUARDIAN_URL/api/guardian/geo/volunteers/2/location?mission_id=2" \
  '{
    "latitude": 34.0522,
    "longitude": -118.2437,
    "address": "At Animal Shelter",
    "timestamp": "'$(date -u +"%Y-%m-%dT%H:%M:%S")'"
  }' "success"

# Get all volunteer locations
test_endpoint "Get All Volunteer Locations" "GET" \
  "$GUARDIAN_URL/api/guardian/geo/volunteers/locations" "" "volunteers"

# Get specific volunteer location
test_endpoint "Get Volunteer 1 Location" "GET" \
  "$GUARDIAN_URL/api/guardian/geo/volunteers/1/location" "" "volunteer"

echo "========================================================================="
echo "4️⃣ HEATMAP & ANALYTICS"
echo "========================================================================="

# Get mission heatmap (all categories)
test_endpoint "Get Mission Heatmap (All)" "GET" \
  "$GUARDIAN_URL/api/guardian/geo/heatmap" "" "points"

# Get heatmap for environment category only
test_endpoint "Get Environment Heatmap" "GET" \
  "$GUARDIAN_URL/api/guardian/geo/heatmap?category=environment" "" "points"

# Get active regions
test_endpoint "Get Active Regions" "GET" \
  "$GUARDIAN_URL/api/guardian/geo/regions" "" "regions"

echo "========================================================================="
echo "5️⃣ NEARBY MISSIONS (Proximity Search)"
echo "========================================================================="

# Find missions near Santa Monica
test_endpoint "Find Missions Near Santa Monica" "GET" \
  "$GUARDIAN_URL/api/guardian/geo/nearby-missions?lat=34.0195&lon=-118.4912&radius_km=5" "" "missions"

# Find missions near Downtown LA (larger radius)
test_endpoint "Find Missions Near Downtown (10km)" "GET" \
  "$GUARDIAN_URL/api/guardian/geo/nearby-missions?lat=34.0522&lon=-118.2437&radius_km=10" "" "missions"

echo "========================================================================="
echo "6️⃣ ROUTE PLANNING"
echo "========================================================================="

# Plan route from Santa Monica to Downtown
test_endpoint "Route: Santa Monica → Downtown" "GET" \
  "$GUARDIAN_URL/api/guardian/geo/route?start_lat=34.0195&start_lon=-118.4912&end_lat=34.0522&end_lon=-118.2437" "" "distance_km"

echo "========================================================================="
echo "7️⃣ GEO STATISTICS"
echo "========================================================================="

# Get geographic statistics
test_endpoint "Get Geo Statistics" "GET" \
  "$GUARDIAN_URL/api/guardian/geo/statistics" "" "total_missions"

echo "========================================================================="
echo "📊 TEST SUMMARY"
echo "========================================================================="

echo ""
echo "Total Tests: $TOTAL_TESTS"
echo -e "${GREEN}Passed: $PASSED_TESTS${NC}"
echo -e "${RED}Failed: $FAILED_TESTS${NC}"
echo ""

if [ $FAILED_TESTS -eq 0 ]; then
    echo -e "${GREEN}🎉 ALL GEO TESTS PASSED!${NC}"
    echo ""
    echo -e "${BLUE}🗺️ Open the interactive map:${NC}"
    echo -e "${BLUE}   http://localhost:8001/static/map.html${NC}"
    echo ""
    exit 0
else
    echo -e "${RED}❌ Some tests failed. Please review the output above.${NC}"
    exit 1
fi
