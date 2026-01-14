#!/bin/bash
# Test: GET /keys - List all minion keys
# Endpoint: GET /keys

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${SCRIPT_DIR}/../lib/common.sh"

test_name="REST Endpoint - GET /keys"
test_endpoint="GET /keys"

print_test_header "${test_name}" "${test_endpoint}"

load_token

response=$(curl -sSk "${API_URL}/keys" \
    -H "Accept: application/json" \
    -H "X-Auth-Token: ${TOKEN}")

print_result "${response}"

print_test_footer
