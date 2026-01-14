#!/bin/bash
# Test: GET /jobs - List all jobs
# Endpoint: GET /jobs

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${SCRIPT_DIR}/../lib/common.sh"

test_name="REST Endpoint - GET /jobs"
test_endpoint="GET /jobs"

print_test_header "${test_name}" "${test_endpoint}"

load_token

response=$(curl -sSk "${API_URL}/jobs" \
    -H "Accept: application/json" \
    -H "X-Auth-Token: ${TOKEN}")

print_result "$(truncate_output "${response}" 20)"

print_test_footer
