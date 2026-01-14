#!/bin/bash
# Test: Key Management - List All Keys
# Endpoint: POST / (client=wheel, fun=key.list_all)

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${SCRIPT_DIR}/../lib/common.sh"

test_name="Key Management - List All Keys"
test_endpoint="POST / (wheel: key.list_all)"

print_test_header "${test_name}" "${test_endpoint}"

load_token

response=$(call_api -d client=wheel -d fun=key.list_all)

print_result "${response}"

print_test_footer
