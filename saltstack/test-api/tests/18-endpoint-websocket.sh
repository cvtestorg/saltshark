#!/bin/bash
# Test: GET /ws - WebSocket Connection
# Endpoint: GET /ws

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${SCRIPT_DIR}/../lib/common.sh"

test_name="REST Endpoint - GET /ws (WebSocket)"
test_endpoint="GET /ws"

print_test_header "${test_name}" "${test_endpoint}"

load_token

print_info "WebSocket endpoint for bidirectional communication"
print_info "WebSocket URL: ws://localhost:8000/ws?token=${TOKEN:0:20}..."
echo ""

# Check if websocat or wscat is available
if command_exists websocat; then
    print_info "Testing WebSocket connection with websocat (5 seconds)..."
    echo ""
    
    # Send a ping message and capture response
    echo '{"ping": "test"}' | timeout 5 websocat "ws://localhost:8000/ws?token=${TOKEN}" 2>&1 || true
    
    echo ""
    print_success "WebSocket connection test completed"
    
elif command_exists wscat; then
    print_info "Testing WebSocket connection with wscat (5 seconds)..."
    echo ""
    
    timeout 5 wscat -c "ws://localhost:8000/ws?token=${TOKEN}" 2>&1 || true
    
    echo ""
    print_success "WebSocket connection test completed"
    
else
    print_warning "WebSocket client not found (websocat or wscat)"
    print_info "Install websocat: brew install websocat (macOS) or cargo install websocat"
    print_info "Install wscat: npm install -g wscat"
    echo ""
    print_info "Manual test command:"
    echo "  websocat \"ws://localhost:8000/ws?token=${TOKEN}\""
    echo "  # or"
    echo "  wscat -c \"ws://localhost:8000/ws?token=${TOKEN}\""
fi

echo ""
print_info "Example JavaScript usage:"
echo "  var ws = new WebSocket('ws://localhost:8000/ws?token=YOUR_TOKEN');"
echo "  ws.onopen = function() {"
echo "    console.log('WebSocket connected');"
echo "    ws.send(JSON.stringify({client: 'local', tgt: '*', fun: 'test.ping'}));"
echo "  };"
echo "  ws.onmessage = function(event) {"
echo "    console.log('Received:', JSON.parse(event.data));"
echo "  };"

print_test_footer
