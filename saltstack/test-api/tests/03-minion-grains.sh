#!/bin/bash
# Test: Get Minion Grains (OS Information)
# Endpoint: POST / (client=local, fun=grains.item)

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${SCRIPT_DIR}/../lib/common.sh"

test_name="Minion Information - Get OS Grains"
test_endpoint="POST / (grains.item)"

print_test_header "${test_name}" "${test_endpoint}"

load_token

response=$(call_api \
    -d client=local \
    -d tgt='*' \
    -d fun=grains.item \
    -d arg=os \
    -d arg=osrelease \
    -d arg=kernel)

print_result "${response}"

print_test_footer
