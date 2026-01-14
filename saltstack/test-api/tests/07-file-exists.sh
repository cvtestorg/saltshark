#!/bin/bash
# Test: File Operations - Check File Existence
# Endpoint: POST / (file.file_exists)

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${SCRIPT_DIR}/../lib/common.sh"

test_name="File Operations - Check File Existence"
test_endpoint="POST / (file.file_exists)"

print_test_header "${test_name}" "${test_endpoint}"

load_token

print_info "Checking: /etc/hosts"

response=$(call_api \
    -d client=local \
    -d tgt='*' \
    -d fun=file.file_exists \
    -d arg=/etc/hosts)

print_result "${response}"

print_test_footer
