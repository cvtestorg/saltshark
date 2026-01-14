# Development Environment

This directory contains Docker Compose configuration for running SaltShark's development environment.

## Services

### PostgreSQL Database
- **Image**: postgres:15-alpine
- **Port**: 5432
- **Database**: saltshark_dev
- **User**: saltshark
- **Password**: password

### OpenFGA (Authorization)
- **Image**: openfga/openfga:latest
- **Ports**: 8080, 8081, 3000
- **Datastore**: In-memory

## Quick Start

### Using Docker Compose

Start all services:
```bash
docker-compose up -d
```

View logs:
```bash
docker-compose logs -f
```

Stop all services:
```bash
docker-compose down
```

### Using Standalone PostgreSQL

If you only need the database:
```bash
./start-postgres.sh
```

## Database Connection

Once PostgreSQL is running, configure your backend `.env`:

```bash
DATABASE_URL=postgresql://saltshark:password@localhost:5432/saltshark_dev
```

## Architecture Changes

**Note**: Redis has been removed to simplify the architecture. The application now uses:
- **PostgreSQL** for persistent data storage
- **JWT** for stateless authentication (no session storage needed)

If you need caching in the future, consider:
- Application-level caching with `functools.lru_cache`
- PostgreSQL query optimization
- Adding Redis back if absolutely necessary

## Data Persistence

Data is stored in Docker volumes:
- `postgres-data`: PostgreSQL database files

To reset the database:
```bash
docker-compose down -v
docker-compose up -d
```

## Troubleshooting

### Port already in use

If port 5432 is already in use:
```bash
# Check what's using the port
lsof -i :5432

# Stop the conflicting service or change the port in docker-compose.yaml
```

### Connection refused

Make sure the database is running:
```bash
docker-compose ps
```

Check the database is healthy:
```bash
docker-compose exec db pg_isready -U saltshark
```
