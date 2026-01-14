#!/bin/bash
# Test: System Resources - Disk Usage
# Endpoint: POST / (disk.usage)

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${SCRIPT_DIR}/../lib/common.sh"

test_name="System Resources - Disk Usage"
test_endpoint="POST / (disk.usage)"

print_test_header "${test_name}" "${test_endpoint}"

load_token

response=$(call_api -d client=local -d tgt='*' -d fun=disk.usage)

print_result "$(truncate_output "${response}" 15)"

print_test_footer
