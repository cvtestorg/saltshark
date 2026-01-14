#!/bin/bash
#
# Run all Salt API tests
#
# This script executes all test scripts in the tests/ directory
# in numerical order.
#

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${SCRIPT_DIR}/lib/colors.sh"
source "${SCRIPT_DIR}/lib/utils.sh"

# Configuration
API_URL="${API_URL:-http://localhost:8000}"
USERNAME="${USERNAME:-salt}"
PASSWORD="${SALT_SHARED_SECRET:-changeme_insecure_default}"

export API_URL USERNAME PASSWORD

# Test counters
TOTAL_TESTS=0
PASSED_TESTS=0
FAILED_TESTS=0
SKIPPED_TESTS=0

# Cleanup function
cleanup() {
    rm -f "${SCRIPT_DIR}/.token" "${SCRIPT_DIR}/.last_jid"
}

# Trap cleanup on exit
trap cleanup EXIT

# Print main header
print_header "Salt API Comprehensive Test Suite"
echo ""
print_info "API URL: ${API_URL}"
print_info "Username: ${USERNAME}"
print_info "Test Directory: ${SCRIPT_DIR}/tests"
echo ""
print_separator

# Find all test scripts
test_scripts=$(find "${SCRIPT_DIR}/tests" -name "*.sh" -type f | sort)

if [[ -z "${test_scripts}" ]]; then
    print_error "No test scripts found in ${SCRIPT_DIR}/tests"
    exit 1
fi

# Run each test
for test_script in ${test_scripts}; do
    ((TOTAL_TESTS++))
    
    test_name=$(basename "${test_script}")
    
    if bash "${test_script}"; then
        ((PASSED_TESTS++))
        print_success "✓ ${test_name}"
    else
        ((FAILED_TESTS++))
        print_error "✗ ${test_name}"
    fi
done

# Print summary
echo ""
print_footer
print_header "Test Summary"
echo ""
echo -e "  ${COLOR_BOLD}Total Tests:${COLOR_RESET}   ${TOTAL_TESTS}"
echo -e "  ${COLOR_BOLD_GREEN}Passed:${COLOR_RESET}        ${PASSED_TESTS}"

if [[ ${FAILED_TESTS} -gt 0 ]]; then
    echo -e "  ${COLOR_BOLD_RED}Failed:${COLOR_RESET}        ${FAILED_TESTS}"
fi

if [[ ${SKIPPED_TESTS} -gt 0 ]]; then
    echo -e "  ${COLOR_BOLD_YELLOW}Skipped:${COLOR_RESET}       ${SKIPPED_TESTS}"
fi

echo ""

# Calculate success rate
if [[ ${TOTAL_TESTS} -gt 0 ]]; then
    success_rate=$((PASSED_TESTS * 100 / TOTAL_TESTS))
    echo -e "  ${COLOR_BOLD}Success Rate:${COLOR_RESET}  ${success_rate}%"
    echo ""
fi

print_info "Additional endpoints to explore:"
echo "  • GET  /events     - Server-Sent Events stream (real-time monitoring)"
echo "  • GET  /ws         - WebSocket endpoint (bidirectional communication)"
echo "  • POST /hook       - Webhook receiver for external integrations"
echo ""
print_info "For more examples, see README.md"
echo ""
print_footer

# Exit with appropriate code
if [[ ${FAILED_TESTS} -gt 0 ]]; then
    exit 1
fi
