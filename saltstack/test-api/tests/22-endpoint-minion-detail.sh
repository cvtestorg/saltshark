#!/bin/bash
# Test: GET /minions/{mid} - Get Specific Minion Details
# Endpoint: GET /minions/{mid}

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${SCRIPT_DIR}/../lib/common.sh"

test_name="REST Endpoint - GET /minions/{mid}"
test_endpoint="GET /minions/{mid}"

print_test_header "${test_name}" "${test_endpoint}"

load_token

# First, get list of minions to find a minion ID
print_info "Getting list of minions..."
minions_response=$(curl -sSk "${API_URL}/minions" \
    -H "Accept: application/json" \
    -H "X-Auth-Token: ${TOKEN}")

# Extract first minion ID
if command_exists jq; then
    minion_id=$(echo "${minions_response}" | jq -r '.return[0] | keys[0] // empty' 2>/dev/null)
else
    # Fallback: try to extract minion ID without jq
    minion_id=$(echo "${minions_response}" | grep -o '"[a-f0-9]\{12\}"' | head -1 | tr -d '"')
fi

if [[ -z "${minion_id}" ]]; then
    print_warning "No minion ID found, cannot test specific minion endpoint"
    print_info "Make sure minions are connected and accepted"
    exit 0
fi

print_success "Found minion: ${minion_id}"
echo ""

# Get specific minion details
print_info "Getting details for minion: ${minion_id}"
response=$(curl -sSk "${API_URL}/minions/${minion_id}" \
    -H "Accept: application/json" \
    -H "X-Auth-Token: ${TOKEN}")

print_result "$(truncate_output "${response}" 20)"

print_test_footer
