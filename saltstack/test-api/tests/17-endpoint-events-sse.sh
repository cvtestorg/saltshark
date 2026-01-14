#!/bin/bash
# Test: GET /events - Server-Sent Events Stream
# Endpoint: GET /events

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${SCRIPT_DIR}/../lib/common.sh"

test_name="REST Endpoint - GET /events (SSE)"
test_endpoint="GET /events"

print_test_header "${test_name}" "${test_endpoint}"

load_token

print_info "Server-Sent Events stream for real-time monitoring"
print_info "This endpoint streams events continuously"
print_warning "Test will run for 5 seconds to capture sample events"
echo ""

# Run curl in background and capture output for 5 seconds
print_info "Connecting to event stream..."
timeout 5 curl -sSNk "${API_URL}/events?token=${TOKEN}" 2>&1 || true

echo ""
echo ""
print_success "Event stream test completed"
print_info "In production, this stream remains open for continuous monitoring"
echo ""
print_info "Example JavaScript usage:"
echo "  var eventSource = new EventSource('/events?token=YOUR_TOKEN');"
echo "  eventSource.onmessage = function(event) {"
echo "    var saltEvent = JSON.parse(event.data);"
echo "    console.log('Salt Event:', saltEvent);"
echo "  };"

print_test_footer
