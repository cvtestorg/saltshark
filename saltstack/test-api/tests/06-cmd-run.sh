#!/bin/bash
# Test: Command Execution - Run Shell Command
# Endpoint: POST / (cmd.run)

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${SCRIPT_DIR}/../lib/common.sh"

test_name="Command Execution - Shell Command"
test_endpoint="POST / (cmd.run)"

print_test_header "${test_name}" "${test_endpoint}"

load_token

print_info "Executing: whoami"

response=$(call_api \
    -d client=local \
    -d tgt='*' \
    -d fun=cmd.run \
    -d arg='whoami')

print_result "${response}"

print_test_footer
