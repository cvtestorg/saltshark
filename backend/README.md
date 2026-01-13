# SaltShark Backend

Backend API server for SaltShark - a modern web UI for SaltStack/SaltProject.

## Features

- 🚀 **FastAPI** - Modern, fast Python web framework
- 🔌 **Salt API Integration** - Connect to SaltStack API
- 📊 **RESTful API** - Clean REST endpoints for frontend
- ✅ **Type Safety** - Full type hints with Pydantic v2
- 🧪 **Tested** - 76%+ test coverage
- 🔒 **CORS Enabled** - Ready for frontend integration

## Installation

### Using pip

```bash
pip install -e .
```

### Using pip with dev dependencies

```bash
pip install -e ".[dev]"
```

## Configuration

Create a `.env` file in the backend directory:

```bash
# Salt API Configuration
SALT_API_URL=http://your-salt-master:8000
SALT_API_USER=saltapi
SALT_API_PASSWORD=your-password

# Application Configuration
CORS_ORIGINS=["http://localhost:3000"]
SECRET_KEY=your-secret-key
```

## Running the Server

### Development

```bash
uvicorn app.main:app --reload --port 8000
```

### Production

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

## API Documentation

Once the server is running, access:

- **Interactive API docs (Swagger)**: http://localhost:8000/docs
- **Alternative API docs (ReDoc)**: http://localhost:8000/redoc

## Testing

Run tests with pytest:

```bash
pytest
```

Run tests with coverage:

```bash
pytest --cov=app --cov-report=term-missing
```

## API Endpoints

### Health Check

- `GET /health` - Health check endpoint

### Minions

- `GET /api/v1/minions` - List all minions
- `GET /api/v1/minions/{minion_id}` - Get minion details
- `GET /api/v1/minions/{minion_id}/grains` - Get minion grains
- `GET /api/v1/minions/{minion_id}/pillars` - Get minion pillars

### Jobs

- `GET /api/v1/jobs` - List all jobs
- `GET /api/v1/jobs/{jid}` - Get job details
- `POST /api/v1/jobs/execute` - Execute a Salt job

## Project Structure

```
backend/
├── app/
│   ├── api/v1/          # API endpoints
│   │   ├── minions.py   # Minion endpoints
│   │   ├── jobs.py      # Job endpoints
│   │   └── grains.py    # Grains/Pillars endpoints
│   ├── core/            # Core configuration
│   │   └── config.py    # Settings and configuration
│   ├── schemas/         # Pydantic models
│   │   ├── minion.py
│   │   ├── job.py
│   │   └── grains.py
│   ├── services/        # Business logic
│   │   └── salt_api.py  # Salt API client
│   └── main.py          # FastAPI application
├── tests/               # Test suite
│   ├── test_api.py      # API endpoint tests
│   └── test_salt_api.py # Salt API client tests
└── pyproject.toml       # Project configuration
```

## Development

### Code Quality

Format code with ruff:

```bash
ruff format .
```

Lint code:

```bash
ruff check .
```

Type check:

```bash
mypy .
```

## Mock Data

The application includes mock data support for development when the Salt API is not available. The mock data includes:

- 3 sample minions (Ubuntu, CentOS, Debian)
- 2 sample jobs (test.ping, state.apply)

## License

MIT
