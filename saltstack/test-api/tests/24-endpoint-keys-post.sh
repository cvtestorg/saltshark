#!/bin/bash
# Test: POST /keys - Accept or Reject Minion Keys
# Endpoint: POST /keys

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${SCRIPT_DIR}/../lib/common.sh"

test_name="REST Endpoint - POST /keys (Accept/Reject)"
test_endpoint="POST /keys"

print_test_header "${test_name}" "${test_endpoint}"

load_token

print_info "This endpoint is used to accept or reject pending minion keys"
echo ""

# Get current keys status
print_info "Getting current keys status..."
keys_response=$(curl -sSk "${API_URL}/keys" \
    -H "Accept: application/json" \
    -H "X-Auth-Token: ${TOKEN}")

print_result "${keys_response}"

echo ""
print_info "Key management operations:"
echo ""
echo "Accept a pending key:"
echo "  curl -X POST http://localhost:8000/keys \\"
echo "    -H 'X-Auth-Token: YOUR_TOKEN' \\"
echo "    -H 'Content-Type: application/json' \\"
echo "    -d '{\"match\": \"minion-id\", \"action\": \"accept\"}'"
echo ""
echo "Reject a pending key:"
echo "  curl -X POST http://localhost:8000/keys \\"
echo "    -H 'X-Auth-Token: YOUR_TOKEN' \\"
echo "    -H 'Content-Type: application/json' \\"
echo "    -d '{\"match\": \"minion-id\", \"action\": \"reject\"}'"
echo ""
echo "Accept all pending keys:"
echo "  curl -X POST http://localhost:8000/keys \\"
echo "    -H 'X-Auth-Token: YOUR_TOKEN' \\"
echo "    -H 'Content-Type: application/json' \\"
echo "    -d '{\"match\": \"*\", \"action\": \"accept\"}'"

print_test_footer
