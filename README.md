# 🦈 SaltShark

A modern, beautiful web UI for SaltStack/SaltProject built with Next.js 16 and FastAPI.

![Dashboard](https://github.com/user-attachments/assets/128796d6-d103-4603-8b5c-5f24e32889d5)

## Features

### Backend (FastAPI + Python)
- ✅ RESTful API for Salt management
- ✅ Salt API client
- ✅ Type-safe with Pydantic v2
- ✅ 76%+ test coverage
- ✅ OpenAPI documentation

### Frontend (Next.js 16 + Shadcn UI)
- ✅ Modern responsive dashboard
- ✅ Minion management and monitoring
- ✅ Job execution and tracking
- ✅ Beautiful UI with Tailwind CSS
- ✅ TypeScript for type safety
- ✅ Real-time status updates

## Quick Start

### Prerequisites

- Python 3.12+
- Node.js 18+
- **SaltStack installation with Salt API enabled** OR Docker/Docker Compose

### SaltStack Testing Environment (Option 1: Docker)

Use the included docker-compose setup for testing:

```bash
cd saltstack
./start.sh
```

This starts:
- Salt Master with rest_cherrypy API on port 8000
- 3 Salt Minions (minion-1, minion-2, minion-3)

API credentials: `saltapi` / `saltapi`

For more options, see [saltstack/README.md](saltstack/README.md)

### SaltStack (Option 2: Existing Installation)

If you have SaltStack already installed and configured, configure the backend to connect to your Salt API.

### Backend Setup

```bash
cd backend
pip install -e .
# Using faster-app (recommended)
faster server start

# Or using uvicorn directly
uvicorn main:app --reload --port 8000
```

The API will be available at http://localhost:8000
- API Docs: http://localhost:8000/docs

### Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

The web UI will be available at http://localhost:3000

## Screenshots

### Dashboard
![Dashboard](https://github.com/user-attachments/assets/128796d6-d103-4603-8b5c-5f24e32889d5)
Monitor your SaltStack infrastructure at a glance.

### Minions Management
![Minions](https://github.com/user-attachments/assets/ab26fd00-8a5d-4ed2-93ec-6908d4c03a77)
View and manage all your Salt minions with status indicators.

### Jobs Monitoring
![Jobs](https://github.com/user-attachments/assets/ba4da9bf-a68b-43a0-9a34-b17756c5a93d)
Track running and completed Salt jobs.

### Execute Jobs
![Execute Job](https://github.com/user-attachments/assets/93d5aa4f-f2e6-49a6-b017-f05db810a94f)
Execute Salt commands with an intuitive interface.

## Architecture

```
saltshark/
├── backend/          # FastAPI backend (faster-app v0.1.7)
│   ├── apps/         # Modular applications (faster-app pattern)
│   ├── api/          # API endpoints
│   ├── schemas/      # Shared data models
│   ├── services/     # Shared business logic
│   ├── core/         # Core configuration
│   ├── main.py       # Application entry point
│   └── tests/        # Backend tests
│
├── saltstack/        # SaltStack testing environment
│   ├── docker-compose.yml  # Salt Master + Minions
│   ├── start.sh     # Quick start script
│   └── master/      # Salt Master config
│
└── frontend/         # Next.js frontend
    ├── app/          # Pages and layouts
    ├── components/   # React components
    ├── lib/          # Utilities
    └── types/        # TypeScript types
```

## Development

### Backend

```bash
# Run tests
cd backend
pytest

# Run with coverage
pytest --cov=app --cov-report=term-missing

# Format code
ruff format .

# Lint
ruff check .
```

### Frontend

```bash
# Run development server
cd frontend
npm run dev

# Build for production
npm run build

# Lint
npm run lint
```

## Configuration

### Backend (.env)

```env
SALT_API_URL=http://localhost:8000
SALT_API_USER=saltapi
SALT_API_PASSWORD=your-password
CORS_ORIGINS=["http://localhost:3000"]
```

### Frontend (.env.local)

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## Features Roadmap

- [x] Dashboard with statistics
- [x] Minion list and status
- [x] Job execution and monitoring
- [x] Mock data for development
- [ ] Real-time updates via WebSockets
- [ ] Authentication and authorization
- [ ] Dark mode support
- [ ] Grains and Pillars viewer
- [ ] State management
- [ ] Event stream monitoring
- [ ] Advanced job scheduling

## Tech Stack

### Backend
- **FastAPI** - Modern Python web framework
- **httpx** - Async HTTP client
- **Pydantic** - Data validation
- **pytest** - Testing framework

### Frontend
- **Next.js 16** - React framework
- **Shadcn UI** - Component library
- **Tailwind CSS** - Styling
- **TypeScript** - Type safety
- **Lucide React** - Icons

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

MIT

## Support

For issues and questions, please open an issue on GitHub.
