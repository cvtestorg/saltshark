#!/bin/bash
# Quick start script for PostgreSQL database using Docker

set -e

echo "🐘 Starting PostgreSQL database for SaltShark..."

# Check if docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Error: Docker not found. Please install Docker first."
    exit 1
fi

# Start PostgreSQL container
docker run -d \
  --name saltshark-postgres \
  -e POSTGRES_USER=saltshark \
  -e POSTGRES_PASSWORD=password \
  -e POSTGRES_DB=saltshark_dev \
  -p 5432:5432 \
  -v saltshark-postgres-data:/var/lib/postgresql/data \
  postgres:15-alpine

echo ""
echo "✅ PostgreSQL started successfully!"
echo ""
echo "Database connection details:"
echo "  Host: localhost"
echo "  Port: 5432"
echo "  Database: saltshark_dev"
echo "  User: saltshark"
echo "  Password: password"
echo ""
echo "Connection URL:"
echo "  postgresql://saltshark:password@localhost:5432/saltshark_dev"
echo ""
echo "To stop the database:"
echo "  docker stop saltshark-postgres"
echo ""
echo "To remove the database:"
echo "  docker rm saltshark-postgres"
echo ""
