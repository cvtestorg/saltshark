#!/bin/bash
# Frontend-Backend Integration Test Script
# Tests key API endpoints to verify frontend-backend connectivity

set -e

API_BASE="http://localhost:8000"

echo "🔍 Testing SaltShark Backend API (faster-app v0.1.6)"
echo "================================================"
echo ""

# Test 1: Health Check
echo "✓ Test 1: Health Check"
HEALTH=$(curl -s ${API_BASE}/api/v1/health)
if echo "$HEALTH" | jq -e '.status == "healthy"' > /dev/null; then
    echo "  ✅ Health endpoint working"
else
    echo "  ❌ Health endpoint failed"
    exit 1
fi

# Test 2: Root Info
echo "✓ Test 2: API Root Info"
ROOT=$(curl -s ${API_BASE}/api/v1/)
if echo "$ROOT" | jq -e '.message' > /dev/null; then
    echo "  ✅ Root endpoint working"
else
    echo "  ❌ Root endpoint failed"
    exit 1
fi

# Test 3: Authentication
echo "✓ Test 3: Authentication"
LOGIN=$(curl -s -X POST ${API_BASE}/api/v1/auth/login \
    -H "Content-Type: application/json" \
    -d '{"username": "admin", "password": "admin123"}')
TOKEN=$(echo "$LOGIN" | jq -r '.access_token')
if [ "$TOKEN" != "null" ] && [ -n "$TOKEN" ]; then
    echo "  ✅ Login successful, token received"
else
    echo "  ❌ Login failed"
    exit 1
fi

# Test 4: Authenticated Endpoint
echo "✓ Test 4: Authenticated User Endpoint"
USER=$(curl -s ${API_BASE}/api/v1/auth/me -H "Authorization: Bearer $TOKEN")
if echo "$USER" | jq -e '.username == "admin"' > /dev/null; then
    echo "  ✅ Authenticated endpoint working"
else
    echo "  ❌ Authenticated endpoint failed"
    exit 1
fi

# Test 5: Runners Endpoint
echo "✓ Test 5: Runners Common Endpoint"
RUNNERS=$(curl -s ${API_BASE}/api/v1/runners/common)
if echo "$RUNNERS" | jq -e '.success == true' > /dev/null; then
    echo "  ✅ Runners endpoint working"
else
    echo "  ❌ Runners endpoint failed"
    exit 1
fi

# Test 6: Orchestration Endpoint
echo "✓ Test 6: Orchestration Common Endpoint"
ORCH=$(curl -s ${API_BASE}/api/v1/orchestration/common)
if echo "$ORCH" | jq -e '.success == true' > /dev/null; then
    echo "  ✅ Orchestration endpoint working"
else
    echo "  ❌ Orchestration endpoint failed"
    exit 1
fi

# Test 7: OpenAPI Spec
echo "✓ Test 7: OpenAPI Specification"
OPENAPI=$(curl -s ${API_BASE}/openapi.json)
if echo "$OPENAPI" | jq -e '.info.title == "SaltShark API"' > /dev/null; then
    echo "  ✅ OpenAPI spec available"
else
    echo "  ❌ OpenAPI spec failed"
    exit 1
fi

echo ""
echo "================================================"
echo "✅ All integration tests passed!"
echo ""
echo "Frontend can now access backend at: ${API_BASE}"
echo "API Documentation: ${API_BASE}/docs"
echo ""
