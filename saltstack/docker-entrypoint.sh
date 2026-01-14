#!/bin/bash
set -e

# Start salt-master in the background
echo "Starting salt-master..."
salt-master -l debug &
MASTER_PID=$!

# Wait for salt-master to initialize
sleep 5

# Start salt-api in the background
echo "Starting salt-api..."
salt-api -l debug &
API_PID=$!

# Function to cleanup on exit
cleanup() {
    echo "Shutting down..."
    kill $MASTER_PID $API_PID 2>/dev/null || true
    wait $MASTER_PID $API_PID 2>/dev/null || true
}

trap cleanup SIGTERM SIGINT EXIT

# Wait for both processes
while kill -0 $MASTER_PID 2>/dev/null && kill -0 $API_PID 2>/dev/null; do
    sleep 2
done

# If we get here, one process has died
echo "ERROR: One of the Salt processes has exited unexpectedly"
exit 1
