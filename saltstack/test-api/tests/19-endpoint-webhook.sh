#!/bin/bash
# Test: POST /hook - Webhook Receiver
# Endpoint: POST /hook/{webhook_id}

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${SCRIPT_DIR}/../lib/common.sh"

test_name="REST Endpoint - POST /hook (Webhook)"
test_endpoint="POST /hook/{webhook_id}"

print_test_header "${test_name}" "${test_endpoint}"

print_info "Webhook receiver for external integrations"
print_info "This endpoint allows external systems to trigger Salt operations"
echo ""

# Test webhook endpoint
webhook_id="test-webhook"
print_info "Sending test webhook to: /hook/${webhook_id}"

response=$(curl -sSk "${API_URL}/hook/${webhook_id}" \
    -H "Content-Type: application/json" \
    -d '{
        "event": "deployment",
        "status": "success",
        "service": "my-app",
        "version": "1.0.0"
    }' 2>&1)

print_result "${response}"

echo ""
print_info "Webhook configuration in Salt:"
echo "  1. Create a reactor configuration in /etc/salt/master.d/reactor.conf"
echo "  2. Map webhook events to Salt states"
echo ""
print_info "Example reactor.conf:"
echo "  reactor:"
echo "    - 'salt/netapi/hook/test-webhook':"
echo "      - /srv/reactor/deploy.sls"
echo ""
print_info "External systems can trigger webhooks:"
echo "  curl -X POST http://localhost:8000/hook/test-webhook \\"
echo "    -H 'Content-Type: application/json' \\"
echo "    -d '{\"event\": \"deployment\", \"status\": \"success\"}'"

print_test_footer
