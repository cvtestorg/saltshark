#!/bin/bash
# Test: POST /minions - Execute Commands on Specific Minions
# Endpoint: POST /minions

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${SCRIPT_DIR}/../lib/common.sh"

test_name="REST Endpoint - POST /minions"
test_endpoint="POST /minions"

print_test_header "${test_name}" "${test_endpoint}"

load_token

print_info "Execute commands on specific minions via POST /minions"
echo ""

# Execute test.ping on all minions
response=$(curl -sSk "${API_URL}/minions" \
    -X POST \
    -H "Accept: application/json" \
    -H "X-Auth-Token: ${TOKEN}" \
    -H "Content-Type: application/json" \
    -d '{
        "tgt": "*",
        "fun": "test.ping"
    }')

print_result "${response}"

print_test_footer
