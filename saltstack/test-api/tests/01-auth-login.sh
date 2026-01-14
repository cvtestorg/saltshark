#!/bin/bash
# Test: Authentication - Login to Salt API
# Endpoint: POST /login

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${SCRIPT_DIR}/../lib/common.sh"

test_name="Authentication - Login"
test_endpoint="POST /login"

print_test_header "${test_name}" "${test_endpoint}"

# Execute test
response=$(curl -sSk "${API_URL}/login" \
    -H "Accept: application/json" \
    -d "username=${USERNAME}" \
    -d "password=${PASSWORD}" \
    -d "eauth=sharedsecret" 2>&1)

# Extract token
TOKEN=$(extract_token "${response}")

if [[ -z "${TOKEN}" ]]; then
    print_error "Failed to authenticate"
    print_result "${response}"
    exit 1
fi

print_success "Successfully authenticated"
print_info "Token: ${TOKEN:0:20}..."

# Save token for other tests
echo "${TOKEN}" > "${TOKEN_FILE}"

print_test_footer
