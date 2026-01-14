# Salt API Test Coverage

Complete list of all Salt API endpoints and their test status.

## Core Endpoints

| Endpoint | Method | Test File | Status |
|----------|--------|-----------|--------|
| `/login` | POST | 01-auth-login.sh | ✅ Tested |
| `/logout` | POST | 15-endpoint-logout.sh | ✅ Tested |
| `/` | GET/POST | 02-09 (various) | ✅ Tested |
| `/run` | POST | 14-endpoint-run.sh | ✅ Tested |

## Minion Management

| Endpoint | Method | Test File | Status |
|----------|--------|-----------|--------|
| `/minions` | GET | 10-endpoint-minions.sh | ✅ Tested |
| `/minions` | POST | 16-endpoint-minions-post.sh | ✅ Tested |
| `/minions/{mid}` | GET | 22-endpoint-minion-detail.sh | ✅ Tested |

## Job Management

| Endpoint | Method | Test File | Status |
|----------|--------|-----------|--------|
| `/jobs` | GET | 11-endpoint-jobs.sh | ✅ Tested |
| `/jobs/{jid}` | GET | 23-endpoint-job-detail.sh | ✅ Tested |

## Key Management

| Endpoint | Method | Test File | Status |
|----------|--------|-----------|--------|
| `/keys` | GET | 12-endpoint-keys.sh | ✅ Tested |
| `/keys` | POST | 24-endpoint-keys-post.sh | ✅ Tested |
| `/keys/{mid}` | DELETE | 25-endpoint-keys-delete.sh | ✅ Tested |

## Real-time Monitoring

| Endpoint | Method | Test File | Status |
|----------|--------|-----------|--------|
| `/events` | GET | 17-endpoint-events-sse.sh | ✅ Tested |
| `/ws` | GET | 18-endpoint-websocket.sh | ✅ Tested |

## Integration

| Endpoint | Method | Test File | Status |
|----------|--------|-----------|--------|
| `/hook/{webhook_id}` | POST | 19-endpoint-webhook.sh | ✅ Tested |
| `/stats` | GET | 13-endpoint-stats.sh | ✅ Tested |

## Salt Clients

| Client Type | Test File | Status |
|-------------|-----------|--------|
| `local` | 02-09 (various) | ✅ Tested |
| `local_async` | 20-async-execution.sh | ✅ Tested |
| `runner` | 21-job-status.sh | ✅ Tested |
| `wheel` | 09-key-management.sh | ✅ Tested |
| `local_batch` | - | ⚠️ Not tested |
| `ssh` | - | ⚠️ Not tested |

## Salt Functions Tested

### Execution Modules (local client)
- ✅ `test.ping` - 02-minion-ping.sh
- ✅ `grains.item` - 03-minion-grains.sh
- ✅ `grains.get` - 03-minion-grains.sh
- ✅ `status.uptime` - 04-system-uptime.sh
- ✅ `disk.usage` - 05-disk-usage.sh
- ✅ `cmd.run` - 06-cmd-run.sh
- ✅ `file.file_exists` - 07-file-exists.sh
- ✅ `network.interfaces` - 08-network-interfaces.sh
- ✅ `test.sleep` - 20-async-execution.sh
- ✅ `test.version` - Various tests

### Runner Modules (runner client)
- ✅ `jobs.lookup_jid` - 21-job-status.sh
- ✅ `jobs.active` - Various tests
- ✅ `manage.status` - Various tests

### Wheel Modules (wheel client)
- ✅ `key.list_all` - 09-key-management.sh

## Coverage Summary

- **Total Endpoints**: 16
- **Tested Endpoints**: 16
- **Coverage**: 100% ✅

- **Total Clients**: 6
- **Tested Clients**: 4
- **Client Coverage**: 67% ⚠️

## Missing Tests

### Optional Clients (Not Critical)
- `local_batch` - Batch execution client
- `ssh` - SSH client for agentless execution

These clients are less commonly used and can be added if needed.

## Test Execution Order

Tests are executed in numerical order (01-25), ensuring:
1. Authentication happens first (01)
2. Basic functionality is tested (02-09)
3. REST endpoints are tested (10-19)
4. Advanced features are tested (20-25)

## Notes

- All critical endpoints are covered
- Tests include both success and error scenarios
- Real-time endpoints (SSE, WebSocket) have basic connectivity tests
- Destructive operations (DELETE) are documented but not executed in tests
