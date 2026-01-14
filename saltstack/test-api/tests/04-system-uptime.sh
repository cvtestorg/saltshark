#!/bin/bash
# Test: System Status - Uptime
# Endpoint: POST / (status.uptime)

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${SCRIPT_DIR}/../lib/common.sh"

test_name="System Status - Uptime"
test_endpoint="POST / (status.uptime)"

print_test_header "${test_name}" "${test_endpoint}"

load_token

response=$(call_api -d client=local -d tgt='*' -d fun=status.uptime)

print_result "$(truncate_output "${response}" 15)"

print_test_footer
