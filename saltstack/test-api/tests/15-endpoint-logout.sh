#!/bin/bash
# Test: POST /logout - Invalidate Token
# Endpoint: POST /logout

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${SCRIPT_DIR}/../lib/common.sh"

test_name="REST Endpoint - POST /logout"
test_endpoint="POST /logout"

print_test_header "${test_name}" "${test_endpoint}"

# Get a fresh token for this test
print_info "Getting a fresh token for logout test..."
login_response=$(curl -sSk "${API_URL}/login" \
    -H "Accept: application/json" \
    -d "username=${USERNAME}" \
    -d "password=${PASSWORD}" \
    -d "eauth=sharedsecret")

test_token=$(extract_token "${login_response}")

if [[ -z "${test_token}" ]]; then
    print_error "Failed to get token for logout test"
    exit 1
fi

print_success "Got token: ${test_token:0:20}..."
echo ""

# Test logout
print_info "Logging out..."
response=$(curl -sSk "${API_URL}/logout" \
    -X POST \
    -H "Accept: application/json" \
    -H "X-Auth-Token: ${test_token}")

print_result "${response}"

echo ""
print_info "Verifying token is invalidated..."

# Try to use the token after logout (should fail)
verify_response=$(curl -sSk "${API_URL}/minions" \
    -H "Accept: application/json" \
    -H "X-Auth-Token: ${test_token}" 2>&1)

if echo "${verify_response}" | grep -q "401\|Unauthorized\|Could not authenticate"; then
    print_success "Token successfully invalidated"
else
    print_warning "Token may still be valid (unexpected)"
    print_result "${verify_response}"
fi

print_test_footer
