#!/bin/bash
# Test: Network - List Interfaces
# Endpoint: POST / (network.interfaces)

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${SCRIPT_DIR}/../lib/common.sh"

test_name="Network - List Interfaces"
test_endpoint="POST / (network.interfaces)"

print_test_header "${test_name}" "${test_endpoint}"

load_token

response=$(call_api -d client=local -d tgt='*' -d fun=network.interfaces)

print_result "$(truncate_output "${response}" 15)"

print_test_footer
