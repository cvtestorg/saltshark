#!/bin/bash
# Test: GET /stats - API performance statistics
# Endpoint: GET /stats

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${SCRIPT_DIR}/../lib/common.sh"

test_name="REST Endpoint - GET /stats"
test_endpoint="GET /stats"

print_test_header "${test_name}" "${test_endpoint}"

load_token

response=$(curl -sSk "${API_URL}/stats" \
    -H "Accept: application/json" \
    -H "X-Auth-Token: ${TOKEN}")

print_result "${response}"

print_test_footer
