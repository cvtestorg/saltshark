# Salt API Test Suite

Comprehensive test suite for Salt API (rest_cherrypy) with modular architecture and independent test scripts.

## Quick Start

### Run All Tests

```bash
cd test-api
./run-all-tests.sh
```

### Run Individual Test

```bash
cd test-api

# First, authenticate
./tests/01-auth-login.sh

# Then run any specific test
./tests/02-minion-ping.sh
./tests/10-endpoint-minions.sh
./tests/20-async-execution.sh
```

## Project Structure

```
test-api/
├── run-all-tests.sh     # Main test runner (executes all tests)
├── tests/               # Individual test scripts (25 tests)
│   ├── 01-auth-login.sh
│   ├── 02-minion-ping.sh
│   ├── 03-minion-grains.sh
│   ├── 04-system-uptime.sh
│   ├── 05-disk-usage.sh
│   ├── 06-cmd-run.sh
│   ├── 07-file-exists.sh
│   ├── 08-network-interfaces.sh
│   ├── 09-key-management.sh
│   ├── 10-endpoint-minions.sh
│   ├── 11-endpoint-jobs.sh
│   ├── 12-endpoint-keys.sh
│   ├── 13-endpoint-stats.sh
│   ├── 14-endpoint-run.sh
│   ├── 15-endpoint-logout.sh
│   ├── 16-endpoint-minions-post.sh
│   ├── 17-endpoint-events-sse.sh
│   ├── 18-endpoint-websocket.sh
│   ├── 19-endpoint-webhook.sh
│   ├── 20-async-execution.sh
│   ├── 21-job-status.sh
│   ├── 22-endpoint-minion-detail.sh
│   ├── 23-endpoint-job-detail.sh
│   ├── 24-endpoint-keys-post.sh
│   └── 25-endpoint-keys-delete.sh
├── lib/                 # Shared libraries
│   ├── colors.sh        # Color definitions
│   ├── utils.sh         # Utility functions
│   ├── api.sh           # API helper functions
│   └── common.sh        # Common test functions
└── README.MD            # This file
```

## Test Categories

### Core Functionality (01-09)
- **01-auth-login.sh** - Login and get authentication token
- **02-minion-ping.sh** - Test minion connectivity
- **03-minion-grains.sh** - Get minion system information
- **04-system-uptime.sh** - Check system uptime
- **05-disk-usage.sh** - Get disk usage information
- **06-cmd-run.sh** - Execute shell commands
- **07-file-exists.sh** - Check file existence
- **08-network-interfaces.sh** - List network interfaces
- **09-key-management.sh** - Manage minion keys (via wheel)

### REST Endpoints - Basic (10-14)
- **10-endpoint-minions.sh** - GET /minions (list all minions)
- **11-endpoint-jobs.sh** - GET /jobs (job history)
- **12-endpoint-keys.sh** - GET /keys (list all keys)
- **13-endpoint-stats.sh** - GET /stats (API statistics)
- **14-endpoint-run.sh** - POST /run (inline authentication)

### REST Endpoints - Auth & Actions (15-16)
- **15-endpoint-logout.sh** - POST /logout (invalidate token)
- **16-endpoint-minions-post.sh** - POST /minions (execute on minions)

### REST Endpoints - Real-time & Integration (17-19)
- **17-endpoint-events-sse.sh** - GET /events (Server-Sent Events stream)
- **18-endpoint-websocket.sh** - GET /ws (WebSocket connection)
- **19-endpoint-webhook.sh** - POST /hook (webhook receiver)

### Advanced Features (20-21)
- **20-async-execution.sh** - Async job execution
- **21-job-status.sh** - Check job status

### REST Endpoints - Details & Management (22-25)
- **22-endpoint-minion-detail.sh** - GET /minions/{mid} (specific minion)
- **23-endpoint-job-detail.sh** - GET /jobs/{jid} (specific job)
- **24-endpoint-keys-post.sh** - POST /keys (accept/reject keys)
- **25-endpoint-keys-delete.sh** - DELETE /keys/{mid} (delete key)

## Architecture

### Independent Test Scripts

Each test is a standalone shell script that:
- Can be run independently
- Has a clear, descriptive name
- Tests a specific API endpoint or feature
- Includes inline documentation
- Follows consistent structure

### Benefits

1. **Easy to Maintain** - Each test is isolated
2. **Easy to Debug** - Run specific tests individually
3. **Easy to Extend** - Add new tests by creating new files
4. **Clear Organization** - Numbered naming shows execution order
5. **Reusable** - Tests can be integrated into CI/CD pipelines

### Test Structure

Each test script follows this pattern:

```bash
#!/bin/bash
# Test: Description
# Endpoint: API endpoint being tested

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${SCRIPT_DIR}/../lib/common.sh"

test_name="Test Name"
test_endpoint="Endpoint"

print_test_header "${test_name}" "${test_endpoint}"

load_token

# Test logic here
response=$(call_api ...)

print_result "${response}"

print_test_footer
```

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `API_URL` | `http://localhost:8000` | Salt API endpoint |
| `USERNAME` | `salt` | API username |
| `SALT_SHARED_SECRET` | `changeme_insecure_default` | API password |

## Adding New Tests

To add a new test:

1. Create a new file in `tests/` directory:
   ```bash
   touch test-api/tests/15-my-new-test.sh
   chmod +x test-api/tests/15-my-new-test.sh
   ```

2. Use the template structure:
   ```bash
   #!/bin/bash
   # Test: My New Feature
   # Endpoint: POST /endpoint
   
   set -euo pipefail
   
   SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
   source "${SCRIPT_DIR}/../lib/common.sh"
   
   test_name="My New Feature"
   test_endpoint="POST /endpoint"
   
   print_test_header "${test_name}" "${test_endpoint}"
   
   load_token
   
   response=$(call_api -d param=value)
   
   print_result "${response}"
   
   print_test_footer
   ```

3. Run it:
   ```bash
   ./tests/15-my-new-test.sh
   ```

## Test Naming Convention

Tests are numbered sequentially to control execution order and group by functionality:

- **01-09**: Core functionality (authentication, minions, system info)
- **10-14**: REST endpoints - basic operations (GET minions, jobs, keys, stats, POST run)
- **15-16**: REST endpoints - authentication & actions (logout, POST minions)
- **17-19**: REST endpoints - real-time & integration (SSE, WebSocket, webhooks)
- **20-21**: Advanced features (async execution, job management)
- **22-25**: REST endpoints - details & management (specific minion/job, key operations)
- **26-29**: Reserved for future tests
- **30-39**: Integration tests (reserved)
- **40-49**: Performance tests (reserved)
- **50-59**: Security tests (reserved)

## Features

### Color-Coded Output

- **Green (✓)** - Success
- **Red (✗)** - Error
- **Yellow (⚠)** - Warning
- **Cyan (ℹ)** - Information

### Automatic Token Management

- `01-auth-login.sh` saves token to `.token` file
- Other tests load token automatically
- Token is cleaned up after test run

### Output Truncation

Long outputs are automatically truncated for readability:
```bash
print_result "$(truncate_output "${response}" 15)"
```

## Troubleshooting

### Authentication Fails

Make sure to run the login test first:
```bash
./tests/01-auth-login.sh
```

### Token Not Found

If you see "Token file not found", run:
```bash
./tests/01-auth-login.sh
```

### API Not Responding

Check that Salt API is running:
```bash
curl http://localhost:8000
```

### Async Tests Fail

Ensure `local_async` is enabled in `master.conf`:
```yaml
netapi_enable_clients:
  - local
  - local_async
  - runner
  - wheel
```

Then restart: `../stop.sh && ../start.sh`

## CI/CD Integration

### Run in CI Pipeline

```yaml
# Example GitHub Actions
- name: Run Salt API Tests
  run: |
    cd test-api
    ./run-all-tests.sh
```

### Run Specific Tests

```bash
# Run only endpoint tests
for test in tests/1*.sh; do
    bash "$test"
done

# Run only async tests
bash tests/20-async-execution.sh
bash tests/21-job-status.sh
```

## Contributing

When adding new tests:

1. Follow the naming convention
2. Use the standard template structure
3. Add inline documentation
4. Test independently before committing
5. Update this README with new test descriptions

## License

This test suite is part of the docker-saltstack project.
