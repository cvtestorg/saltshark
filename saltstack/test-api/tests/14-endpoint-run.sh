#!/bin/bash
# Test: POST /run - Execute with inline authentication
# Endpoint: POST /run

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${SCRIPT_DIR}/../lib/common.sh"

test_name="REST Endpoint - POST /run (inline auth)"
test_endpoint="POST /run"

print_test_header "${test_name}" "${test_endpoint}"

print_info "This endpoint allows authentication in the same request"

response=$(curl -sSk "${API_URL}/run" \
    -H "Accept: application/json" \
    -d "username=${USERNAME}" \
    -d "password=${PASSWORD}" \
    -d "eauth=sharedsecret" \
    -d "client=local" \
    -d "tgt=*" \
    -d "fun=test.ping")

print_result "${response}"

print_test_footer
