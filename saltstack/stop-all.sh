#!/bin/bash
set -e
echo "Stopping all Salt services..."
if [ "$EUID" -ne 0 ]; then 
    echo "Error: Must run as root"
    exit 1
fi
# Stop salt-api
if pgrep -x "salt-api" > /dev/null; then
    echo "Stopping salt-api..."
    kill -9 $(pgrep -x "salt-api") 2>/dev/null || true
fi
# Stop salt-master
if pgrep -x "salt-master" > /dev/null; then
    echo "Stopping salt-master..."
    kill -9 $(pgrep -x "salt-master") 2>/dev/null || true
fi
# Stop all salt-minion processes
if pgrep -x "salt-minion" > /dev/null; then
    echo "Stopping salt-minion(s)..."
    kill -9 $(pgrep -x "salt-minion") 2>/dev/null || true
fi
echo "✅ All Salt services stopped!"
