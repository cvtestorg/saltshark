#!/bin/bash
# Test: DELETE /keys/{mid} - Delete Minion Key
# Endpoint: DELETE /keys/{mid}

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${SCRIPT_DIR}/../lib/common.sh"

test_name="REST Endpoint - DELETE /keys/{mid}"
test_endpoint="DELETE /keys/{mid}"

print_test_header "${test_name}" "${test_endpoint}"

load_token

print_info "This endpoint deletes a minion key"
print_warning "This is a destructive operation - not executing in test"
echo ""

# Get current keys
print_info "Getting current keys..."
keys_response=$(curl -sSk "${API_URL}/keys" \
    -H "Accept: application/json" \
    -H "X-Auth-Token: ${TOKEN}")

print_result "${keys_response}"

echo ""
print_info "To delete a minion key:"
echo "  curl -X DELETE http://localhost:8000/keys/MINION_ID \\"
echo "    -H 'X-Auth-Token: YOUR_TOKEN' \\"
echo "    -H 'Accept: application/json'"
echo ""
print_warning "Note: Deleting a key will prevent the minion from communicating"
print_info "The minion will need to re-authenticate and have its key accepted again"

print_test_footer
