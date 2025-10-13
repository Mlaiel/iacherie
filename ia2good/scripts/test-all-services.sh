#!/bin/bash

set -e

echo "============================================================"
echo "🧪 E2E TEST - ALL MICROSERVICES"
echo "============================================================"

# Configuration
export IACHERIE_API_URL="http://localhost:8000"
export IACHERIE_API_KEY="test-key-e2e"
export DATABASE_URL="sqlite:///test.db"
export PYTHONPATH="/workspaces/iacherie/ia2good/shared-services:$PYTHONPATH"

GUARDIAN_PORT=8001
EDUVERIFY_PORT=8002
MEDCARE_PORT=8003
TEST_DURATION=10

# Cleanup function
cleanup() {
    echo ""
    echo "🧹 Cleaning up..."
    pkill -f "uvicorn.*guardian" 2>/dev/null || true
    pkill -f "uvicorn.*eduverify" 2>/dev/null || true
    pkill -f "uvicorn.*medcare" 2>/dev/null || true
    rm -f /tmp/guardian.log /tmp/eduverify.log /tmp/medcare.log
}

trap cleanup EXIT

# Start services
echo ""
echo "🚀 Starting microservices..."

# Guardian
cd /workspaces/iacherie/ia2good/microservices/ia2good
python3 -m uvicorn main:app --host 127.0.0.1 --port $GUARDIAN_PORT --log-level warning > /tmp/guardian.log 2>&1 &
GUARDIAN_PID=$!
echo "  ✅ Guardian started (PID: $GUARDIAN_PID, Port: $GUARDIAN_PORT)"

# EduVerify
cd /workspaces/iacherie/ia2good/microservices/eduverify
python3 -m uvicorn main:app --host 127.0.0.1 --port $EDUVERIFY_PORT --log-level warning > /tmp/eduverify.log 2>&1 &
EDUVERIFY_PID=$!
echo "  ✅ EduVerify started (PID: $EDUVERIFY_PID, Port: $EDUVERIFY_PORT)"

# MedCare
cd /workspaces/iacherie/ia2good/microservices/medcare-ai
python3 -m uvicorn main:app --host 127.0.0.1 --port $MEDCARE_PORT --log-level warning > /tmp/medcare.log 2>&1 &
MEDCARE_PID=$!
echo "  ✅ MedCare started (PID: $MEDCARE_PID, Port: $MEDCARE_PORT)"

# Wait for services to start
echo ""
echo "⏳ Waiting for services to initialize (5 seconds)..."
sleep 5

# Test function
test_endpoint() {
    local service=$1
    local url=$2
    local expected_code=${3:-200}
    
    response=$(curl -s -w "\n%{http_code}" "$url" 2>/dev/null)
    http_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | head -n-1)
    
    if [ "$http_code" == "$expected_code" ]; then
        echo "    ✅ $service: $url (HTTP $http_code)"
        return 0
    else
        echo "    ❌ $service: $url (HTTP $http_code, expected $expected_code)"
        return 1
    fi
}

# Run tests
echo ""
echo "🧪 Testing endpoints..."
echo ""

TOTAL_TESTS=0
PASSED_TESTS=0

# Guardian Tests
echo "  📦 GUARDIAN API (Port $GUARDIAN_PORT):"
TOTAL_TESTS=$((TOTAL_TESTS + 3))
test_endpoint "Health" "http://localhost:$GUARDIAN_PORT/health" && PASSED_TESTS=$((PASSED_TESTS + 1))
test_endpoint "Ready" "http://localhost:$GUARDIAN_PORT/ready" && PASSED_TESTS=$((PASSED_TESTS + 1))
test_endpoint "AI Health" "http://localhost:$GUARDIAN_PORT/api/guardian/ai/health-check" && PASSED_TESTS=$((PASSED_TESTS + 1))

# EduVerify Tests
echo ""
echo "  📦 EDUVERIFY API (Port $EDUVERIFY_PORT):"
TOTAL_TESTS=$((TOTAL_TESTS + 3))
test_endpoint "Health" "http://localhost:$EDUVERIFY_PORT/health" && PASSED_TESTS=$((PASSED_TESTS + 1))
test_endpoint "Ready" "http://localhost:$EDUVERIFY_PORT/ready" && PASSED_TESTS=$((PASSED_TESTS + 1))
test_endpoint "AI Health" "http://localhost:$EDUVERIFY_PORT/api/eduverify/ai/health-check" && PASSED_TESTS=$((PASSED_TESTS + 1))

# MedCare Tests
echo ""
echo "  📦 MEDCARE API (Port $MEDCARE_PORT):"
TOTAL_TESTS=$((TOTAL_TESTS + 3))
test_endpoint "Health" "http://localhost:$MEDCARE_PORT/health" && PASSED_TESTS=$((PASSED_TESTS + 1))
test_endpoint "Ready" "http://localhost:$MEDCARE_PORT/ready" && PASSED_TESTS=$((PASSED_TESTS + 1))
test_endpoint "AI Health" "http://localhost:$MEDCARE_PORT/api/medcare/ai/health-check" && PASSED_TESTS=$((PASSED_TESTS + 1))

# Summary
echo ""
echo "============================================================"
echo "📊 TEST RESULTS"
echo "============================================================"
echo "  Total Tests: $TOTAL_TESTS"
echo "  Passed: $PASSED_TESTS"
echo "  Failed: $((TOTAL_TESTS - PASSED_TESTS))"
echo ""

if [ $PASSED_TESTS -eq $TOTAL_TESTS ]; then
    echo "✅ ALL TESTS PASSED - 100% FUNCTIONAL"
    echo "============================================================"
    exit 0
else
    echo "❌ SOME TESTS FAILED"
    echo ""
    echo "📋 Service Logs:"
    echo ""
    echo "Guardian Log (last 20 lines):"
    tail -20 /tmp/guardian.log 2>/dev/null || echo "No logs"
    echo ""
    echo "EduVerify Log (last 20 lines):"
    tail -20 /tmp/eduverify.log 2>/dev/null || echo "No logs"
    echo ""
    echo "MedCare Log (last 20 lines):"
    tail -20 /tmp/medcare.log 2>/dev/null || echo "No logs"
    echo "============================================================"
    exit 1
fi
