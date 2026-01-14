#!/bin/bash
# Test: Async Job Execution
# Endpoint: POST / (client=local_async)

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${SCRIPT_DIR}/../lib/common.sh"

test_name="Async Execution - Submit Background Job"
test_endpoint="POST / (client=local_async)"

print_test_header "${test_name}" "${test_endpoint}"

load_token

print_info "Submitting async job: test.sleep 2"

response=$(call_api \
    -d client=local_async \
    -d tgt='*' \
    -d fun=test.sleep \
    -d arg=2 2>&1)

if is_valid_json "${response}"; then
    print_success "Job submitted successfully"
    print_result "${response}"
    
    # Try to extract JID
    if command_exists jq; then
        jid=$(echo "${response}" | jq -r '.return[0].jid // empty' 2>/dev/null)
        if [[ -n "${jid}" ]]; then
            print_info "Job ID: ${jid}"
            echo "${jid}" > "${LIB_DIR}/../.last_jid"
        fi
    fi
else
    print_warning "Async execution failed"
    print_info "Ensure 'local_async' is enabled in master.conf"
    print_result "${response}"
    exit 1
fi

print_test_footer
