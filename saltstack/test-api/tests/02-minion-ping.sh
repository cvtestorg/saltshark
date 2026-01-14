#!/bin/bash
# Test: Minion Connectivity - test.ping
# Endpoint: POST / (client=local, fun=test.ping)

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${SCRIPT_DIR}/../lib/common.sh"

test_name="Minion Connectivity - test.ping"
test_endpoint="POST / (client=local)"

print_test_header "${test_name}" "${test_endpoint}"

# Get token
load_token

# Execute test
response=$(call_api -d client=local -d tgt='*' -d fun=test.ping)

print_result "${response}"

print_test_footer
