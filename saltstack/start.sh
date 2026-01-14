#!/bin/bash
set -e
echo "🦈 SaltShark - Starting SaltStack Test Environment"
if ! command -v docker-compose &> /dev/null && ! command -v docker compose &> /dev/null; then
    echo "❌ Error: docker-compose not found."
    exit 1
fi
if command -v docker compose &> /dev/null; then
    DOCKER_COMPOSE="docker compose"
else
    DOCKER_COMPOSE="docker-compose"
fi
echo "📦 Starting containers..."
$DOCKER_COMPOSE up -d
echo "⏳ Waiting for services..."
sleep 5
echo "✅ SaltStack environment is ready!"
echo "API: http://localhost:8000"
echo "Credentials: saltapi/saltapi"
