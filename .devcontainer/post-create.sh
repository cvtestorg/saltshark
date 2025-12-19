#!/bin/bash
set -e

echo "🚀 Starting post-create setup..."

# Fix permissions for uv cache if needed
mkdir -p /home/vscode/.cache/uv
chown -R vscode:vscode /home/vscode/.cache

# Backend setup
if [ -d "backend" ]; then
    echo "📦 Setting up Backend (Python/UV)..."
    cd backend
    if [ -f "pyproject.toml" ]; then
        # Create .env from example if not exists
        if [ ! -f ".env" ] && [ -f ".env.example" ]; then
            echo "📄 Creating backend/.env from .env.example..."
            cp .env.example .env
        fi
        
        # Create virtual environment and install dependencies
        uv sync
        echo "✅ Backend dependencies installed."
    else
        echo "⚠️ backend/pyproject.toml not found, skipping dependency install."
    fi
    cd ..
fi

# Frontend setup
if [ -d "frontend" ]; then
    echo "📦 Setting up Frontend (Node/pnpm)..."
    cd frontend
    if [ -f "package.json" ]; then
        pnpm install
        echo "✅ Frontend dependencies installed."
    else
        echo "⚠️ frontend/package.json not found, skipping dependency install."
    fi
    cd ..
fi

# Install pre-commit if config exists
if [ -f ".pre-commit-config.yaml" ]; then
    echo "🔒 Installing pre-commit hooks..."
    uv tool install pre-commit
    /home/vscode/.local/bin/pre-commit install
fi

echo "🎉 Dev environment setup complete! You are ready to code."
