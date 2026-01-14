# SaltStack Testing Environment

This directory contains scripts and configuration for running a local SaltStack environment for testing SaltShark.

## Features

- 🚀 Quick start with docker-compose
- 🔧 Multiple minions for testing
- 🌐 rest_cherrypy API enabled
- 📊 Pre-configured with test data

## Quick Start

### Using Docker Compose (Recommended)

```bash
# Start the entire Salt environment
docker-compose up -d

# View logs
docker-compose logs -f

# Stop the environment
docker-compose down
```

This will start:
- **salt-master**: SaltStack master with rest_cherrypy API enabled on port 8000
- **salt-minion-1**: First minion (minion-1)
- **salt-minion-2**: Second minion (minion-2)
- **salt-minion-3**: Third minion (minion-3)

### Using Local Scripts

If you have SaltStack installed locally:

```bash
# Start salt-master with rest_cherrypy
./start-master.sh

# Start multiple minions
./start-minions.sh 3  # Start 3 minions

# Stop all
./stop-all.sh
```

## Configuration

### Salt API Credentials

Default credentials for the rest_cherrypy API:
- **Username**: `saltapi`
- **Password**: `saltapi`
- **URL**: `http://localhost:8000`

### Minion Names

Minions are named sequentially:
- minion-1
- minion-2
- minion-3
- etc.

## Testing SaltShark

Once the environment is running, you can:

1. **Start the SaltShark backend**:
   ```bash
   cd ../backend
   uvicorn app.main:app --reload --port 8001
   ```

2. **Configure backend** to connect to the local Salt API:
   ```bash
   # Create/edit backend/.env
   SALT_API_URL=http://localhost:8000
   SALT_API_USER=saltapi
   SALT_API_PASSWORD=saltapi
   ```

3. **Test the connection**:
   ```bash
   curl http://localhost:8001/api/v1/minions
   ```

## Docker Images

The docker-compose setup uses:
- `saltstack/salt:latest` - Official SaltStack image
- Configured with rest_cherrypy, pam authentication, and auto-accept keys

## Directory Structure

```
saltstack/
├── README.md              # This file
├── docker-compose.yml     # Docker compose configuration
├── master/                # Master configuration
│   └── master.conf        # Salt master config
├── api/                   # API configuration
│   └── api.conf           # rest_cherrypy config
└── minion/                # Minion configuration templates
    └── minion.conf        # Base minion config
```

## Troubleshooting

### Minions not connecting

Check master logs:
```bash
docker-compose logs salt-master
```

Accept keys manually:
```bash
docker-compose exec salt-master salt-key -A -y
```

### API not accessible

Verify the API is running:
```bash
curl http://localhost:8000
```

Check master configuration:
```bash
docker-compose exec salt-master cat /etc/salt/master.d/api.conf
```

### Reset environment

```bash
docker-compose down -v
docker-compose up -d
```

## Advanced Usage

### Adding more minions

Edit `docker-compose.yml` and add more minion services:

```yaml
salt-minion-4:
  image: saltstack/salt:latest
  container_name: salt-minion-4
  hostname: minion-4
  # ... same config as other minions
```

### Custom minion configuration

Mount custom config files:

```yaml
volumes:
  - ./minion/custom.conf:/etc/salt/minion.d/custom.conf:ro
```

## References

- [SaltStack Documentation](https://docs.saltproject.io/)
- [rest_cherrypy API](https://docs.saltproject.io/en/latest/ref/netapi/all/salt.netapi.rest_cherrypy.html)
- [SaltShark Documentation](../README.md)
