# docker-saltstack

Docker Compose setup to spin up a Salt master and minions with the latest SaltProject version.

## Current Version

This project now uses **Salt 3007.11** (latest stable release as of January 2026), installed via PyPI in a Python virtual environment. This approach provides:
- Modern "onedir-style" packaging with isolated dependencies
- Latest security updates and features
- Ubuntu 24.04 LTS base image
- Easy version management and upgrades

## Quick Start

You can read a full article describing how to use this setup [here](https://medium.com/@timlwhite/the-simplest-way-to-learn-saltstack-cd9f5edbc967).

You will need a system with Docker and Docker Compose installed to use this project.

Just run:

`./start.sh`

from a checkout of this directory, and the master and minion will start up with debug logging to the console.

To stop the services, run:

`./stop.sh`

**Note:** After modifying `master.conf`, you must restart the services for changes to take effect:

```bash
./stop.sh && ./start.sh
```

Then you can run (in a separate shell window):

`./master-login.sh`

and it will log you into the command line of the salt-master server.

From that command line you can run something like:

`salt '*' test.ping`

and in the window where you started the services, you will see the log output of both the master sending the command and the minion receiving the command and replying.

To stop the services, run:

`./stop.sh`

[The Salt Remote Execution Tutorial](https://docs.saltproject.io/en/latest/topics/tutorials/modules.html) has some quick examples of the commands you can run from the master.

Note: you will see log messages like : "Could not determine init system from command line" - those are just because salt is running in the foreground and not from an auto-startup.

The salt-master is set up to accept all minions that try to connect.  Since the network that the salt-master sees is only the docker-compose network, this means that only minions within this docker-compose service network will be able to connect (and not random other minions external to docker).

#### Running multiple minions:

`./start.sh 2`

This will start up two minions instead of just one. You can specify any number as the argument to scale the minions.

#### Host Names
The **hostnames** match the names of the containers - so the master is `salt-master` and the minion is `salt-minion`.

If you are running more than one minion with `--scale=2`, you will need to use `docker-saltstack_salt-minion_1` and `docker-saltstack_salt-minion_2` for the minions if you want to target them individually.

## What's New

### 2026 Update

- **Upgraded to Salt 3007.11** - Latest stable version with all recent security patches and features
- **Ubuntu 24.04 LTS** - Modern, long-term supported base OS
- **Modern packaging** - Uses Python virtual environment with PyPI installation for better isolation
- **Improved Dockerfiles** - Cleaner, more maintainable configuration
- **Salt API Enabled** - REST API exposed on port 8000 for external automation and integration

### Migration from Old Version

The old setup used Ubuntu 18.04 and Salt installed from the deprecated `repo.saltstack.com` repository. The new version:
- Uses official PyPI packages
- Provides better security and maintainability  
- Maintains backward compatibility with existing Salt states and configurations
- Adds Salt API for programmatic access

## Salt API Usage

The Salt Master now includes the Salt API (rest_cherrypy) exposed on port 8000. This allows you to control Salt programmatically from external applications.

### Quick API Examples

**1. Login and get a token:**
```bash
curl -sSk http://localhost:8000/login \
  -H "Accept: application/json" \
  -d username=salt \
  -d password=changeme_insecure_default \
  -d eauth=sharedsecret
```

**2. Execute commands using the token:**
```bash
# Replace YOUR_TOKEN with the token from login response
curl -sSk http://localhost:8000 \
  -H "Accept: application/json" \
  -H "X-Auth-Token: YOUR_TOKEN" \
  -d client=local \
  -d tgt='*' \
  -d fun=test.ping
```

**3. Get minion status:**
```bash
curl -sSk http://localhost:8000 \
  -H "Accept: application/json" \
  -H "X-Auth-Token: YOUR_TOKEN" \
  -d client=local \
  -d tgt='*' \
  -d fun=status.uptime
```

### Security Configuration

**⚠️ IMPORTANT FOR PRODUCTION:**

The default configuration uses:
- HTTP (not HTTPS) - `disable_ssl: True`
- Shared secret authentication with default password `changeme_insecure_default`

**For production environments, you should:**

1. **Enable SSL/TLS:**
   - Generate SSL certificates
   - Update `/etc/salt/master` to use `ssl_crt` and `ssl_key`
   - Remove `disable_ssl: True`

2. **Use secure authentication:**
   - Change the shared secret by setting `SALT_SHARED_SECRET` environment variable
   - Or switch to PAM authentication for user-based access control
   - Configure granular permissions in `external_auth`

3. **Example with custom secret:**
```bash
SALT_SHARED_SECRET=your_secure_secret_here ./start.sh
```

### API Documentation

For full API documentation, see:
- [Salt API Documentation](https://docs.saltproject.io/en/latest/ref/netapi/all/salt.netapi.rest_cherrypy.html)
- [External Authentication](https://docs.saltproject.io/en/latest/topics/eauth/index.html)

### Available API Endpoints

The rest_cherrypy module provides the following endpoints:

**Core Endpoints:**
- `POST /login` - Authenticate and get a token
- `POST /logout` - Invalidate the current token
- `GET/POST /` - Execute Salt commands (main endpoint)
- `POST /run` - Alternative endpoint for command execution

**Minion Management:**
- `GET /minions` - List all minions and their details
- `POST /minions` - Execute commands on specific minions
- `GET /minions/{mid}` - Get details for a specific minion

**Job Management:**
- `GET /jobs` - List all jobs
- `GET /jobs/{jid}` - Get details for a specific job

**Key Management:**
- `GET /keys` - List all keys (accepted, pending, rejected)
- `POST /keys` - Accept or reject minion keys
- `DELETE /keys/{mid}` - Delete a minion key

**Real-time Monitoring:**
- `GET /events` - Server-Sent Events (SSE) stream for real-time event monitoring
- `GET /ws` - WebSocket endpoint for bidirectional communication

**Integration:**
- `POST /hook` - Webhook receiver for external integrations
- `GET /stats` - API performance statistics

### API Test Suite

A comprehensive, modular test suite with independent test scripts for each API endpoint:

```bash
cd test-api

# Run all tests
./run-all-tests.sh

# Or run individual tests
./tests/01-auth-login.sh
./tests/02-minion-ping.sh
./tests/10-endpoint-minions.sh
```

**Test Suite Features:**
- **Independent test scripts** - Each endpoint has its own test file
- **Easy to maintain** - Add/modify tests without affecting others
- **Color-coded output** - Clear visual feedback (success, errors, warnings)
- **Modular architecture** - Shared libraries for common functionality
- **CI/CD ready** - Can be integrated into automated pipelines

**Test Categories:**
- **01-09**: Core functionality (auth, minions, system info)
- **10-19**: REST endpoints (/minions, /jobs, /keys, /stats)
- **20-29**: Advanced features (async execution, job management)

See `test-api/README.MD` for detailed documentation.

### More API Examples

**Get disk usage:**
```bash
curl -sSk http://localhost:8000 \
  -H "Accept: application/json" \
  -H "X-Auth-Token: YOUR_TOKEN" \
  -d client=local \
  -d tgt='*' \
  -d fun=disk.usage
```

**Check memory info:**
```bash
curl -sSk http://localhost:8000 \
  -H "Accept: application/json" \
  -H "X-Auth-Token: YOUR_TOKEN" \
  -d client=local \
  -d tgt='*' \
  -d fun=status.meminfo
```

**Execute shell commands:**
```bash
curl -sSk http://localhost:8000 \
  -H "Accept: application/json" \
  -H "X-Auth-Token: YOUR_TOKEN" \
  -d client=local \
  -d tgt='*' \
  -d fun=cmd.run \
  -d arg='ls -la /tmp'
```

**List network interfaces:**
```bash
curl -sSk http://localhost:8000 \
  -H "Accept: application/json" \
  -H "X-Auth-Token: YOUR_TOKEN" \
  -d client=local \
  -d tgt='*' \
  -d fun=network.interfaces
```

**Check if file exists:**
```bash
curl -sSk http://localhost:8000 \
  -H "Accept: application/json" \
  -H "X-Auth-Token: YOUR_TOKEN" \
  -d client=local \
  -d tgt='*' \
  -d fun=file.file_exists \
  -d arg=/etc/hosts
```

**Target specific minions:**
```bash
# Target by exact name
curl -sSk http://localhost:8000 \
  -H "Accept: application/json" \
  -H "X-Auth-Token: YOUR_TOKEN" \
  -d client=local \
  -d tgt='salt-minion' \
  -d fun=test.ping

# Target with glob pattern
curl -sSk http://localhost:8000 \
  -H "Accept: application/json" \
  -H "X-Auth-Token: YOUR_TOKEN" \
  -d client=local \
  -d tgt='salt-*' \
  -d fun=test.ping
```

**Async job execution:**
```bash
# Submit async job
curl -sSk http://localhost:8000 \
  -H "Accept: application/json" \
  -H "X-Auth-Token: YOUR_TOKEN" \
  -d client=local_async \
  -d tgt='*' \
  -d fun=test.sleep \
  -d arg=5

# Check job status (replace JID with actual job ID from response)
curl -sSk http://localhost:8000 \
  -H "Accept: application/json" \
  -H "X-Auth-Token: YOUR_TOKEN" \
  -d client=runner \
  -d fun=jobs.lookup_jid \
  -d arg=20260114123456789012
```

**Manage minion keys:**
```bash
# List all keys
curl -sSk http://localhost:8000 \
  -H "Accept: application/json" \
  -H "X-Auth-Token: YOUR_TOKEN" \
  -d client=wheel \
  -d fun=key.list_all
```

### Advanced API Features

**Real-time Event Streaming (SSE):**

Monitor Salt events in real-time using Server-Sent Events:

```bash
# Stream all events (requires token)
curl -sSNk "http://localhost:8000/events?token=YOUR_TOKEN"

# In JavaScript/Browser:
var eventSource = new EventSource('/events?token=YOUR_TOKEN');
eventSource.onmessage = function(event) {
  var saltEvent = JSON.parse(event.data);
  console.log('Salt Event:', saltEvent);
};
```

**WebSocket Connection:**

For bidirectional communication:

```bash
# Connect via WebSocket (ws:// or wss://)
wscat -c "ws://localhost:8000/ws?token=YOUR_TOKEN"
```

**Webhook Integration:**

Receive webhooks from external systems:

```bash
# External system sends webhook
curl -sSk http://localhost:8000/hook/my-webhook \
  -H "Content-Type: application/json" \
  -d '{"event": "deployment", "status": "success"}'
```

**Get Minion Details:**

```bash
# List all minions with details
curl -sSk http://localhost:8000/minions \
  -H "Accept: application/json" \
  -H "X-Auth-Token: YOUR_TOKEN"

# Get specific minion details
curl -sSk http://localhost:8000/minions/MINION_ID \
  -H "Accept: application/json" \
  -H "X-Auth-Token: YOUR_TOKEN"
```

**Job History:**

```bash
# Get all jobs
curl -sSk http://localhost:8000/jobs \
  -H "Accept: application/json" \
  -H "X-Auth-Token: YOUR_TOKEN"

# Get specific job details
curl -sSk http://localhost:8000/jobs/JOB_ID \
  -H "Accept: application/json" \
  -H "X-Auth-Token: YOUR_TOKEN"
```

**API Statistics:**

```bash
# Get API performance stats
curl -sSk http://localhost:8000/stats \
  -H "Accept: application/json" \
  -H "X-Auth-Token: YOUR_TOKEN"
```

**Alternative /run Endpoint:**

The `/run` endpoint allows authentication in the same request:

```bash
curl -sSk http://localhost:8000/run \
  -H "Accept: application/json" \
  -d username=salt \
  -d password=changeme_insecure_default \
  -d eauth=sharedsecret \
  -d client=local \
  -d tgt='*' \
  -d fun=test.ping
```
