FROM mcr.microsoft.com/devcontainers/python:1-3.11-bullseye

# Install basic tools and clients
RUN apt-get update && export DEBIAN_FRONTEND=noninteractive \
    && apt-get -y install --no-install-recommends \
    postgresql-client \
    redis-tools \
    iputils-ping \
    vim \
    && apt-get clean -y && rm -rf /var/lib/apt/lists/*

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

# Set up working directory
WORKDIR /workspaces/saltshark
