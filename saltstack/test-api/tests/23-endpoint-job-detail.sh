#!/bin/bash
# Test: GET /jobs/{jid} - Get Specific Job Details
# Endpoint: GET /jobs/{jid}

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${SCRIPT_DIR}/../lib/common.sh"

test_name="REST Endpoint - GET /jobs/{jid}"
test_endpoint="GET /jobs/{jid}"

print_test_header "${test_name}" "${test_endpoint}"

load_token

# Check if we have a saved JID from async test
jid_file="${LIB_DIR}/../.last_jid"
if [[ -f "${jid_file}" ]]; then
    jid=$(cat "${jid_file}")
    print_info "Using saved Job ID: ${jid}"
else
    # Get list of jobs and extract first JID
    print_info "Getting list of jobs to find a JID..."
    jobs_response=$(curl -sSk "${API_URL}/jobs" \
        -H "Accept: application/json" \
        -H "X-Auth-Token: ${TOKEN}")
    
    if command_exists jq; then
        jid=$(echo "${jobs_response}" | jq -r '.return[0] | keys[0] // empty' 2>/dev/null)
    else
        # Fallback: try to extract JID without jq
        jid=$(echo "${jobs_response}" | grep -o '"[0-9]\{20\}"' | head -1 | tr -d '"')
    fi
    
    if [[ -z "${jid}" ]]; then
        print_warning "No job ID found, cannot test specific job endpoint"
        print_info "Run some commands first to create jobs"
        exit 0
    fi
    
    print_success "Found Job ID: ${jid}"
fi

echo ""

# Get specific job details
print_info "Getting details for Job ID: ${jid}"
response=$(curl -sSk "${API_URL}/jobs/${jid}" \
    -H "Accept: application/json" \
    -H "X-Auth-Token: ${TOKEN}")

print_result "$(truncate_output "${response}" 20)"

print_test_footer
