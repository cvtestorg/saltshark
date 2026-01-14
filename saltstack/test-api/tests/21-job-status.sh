#!/bin/bash
# Test: Check Job Status
# Endpoint: POST / (client=runner, fun=jobs.lookup_jid)

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${SCRIPT_DIR}/../lib/common.sh"

test_name="Job Management - Check Job Status"
test_endpoint="POST / (jobs.lookup_jid)"

print_test_header "${test_name}" "${test_endpoint}"

load_token

# Get last JID
jid_file="${LIB_DIR}/../.last_jid"
if [[ ! -f "${jid_file}" ]]; then
    print_warning "No job ID found. Run 20-async-execution.sh first."
    exit 1
fi

jid=$(cat "${jid_file}")
print_info "Checking status for Job ID: ${jid}"
print_info "Waiting 3 seconds for job to complete..."
sleep 3

response=$(call_api \
    -d client=runner \
    -d fun=jobs.lookup_jid \
    -d arg="${jid}")

print_result "${response}"

print_test_footer
