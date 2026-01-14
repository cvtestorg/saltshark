#!/bin/bash
COUNT=${1:-1}
docker compose up --scale salt-minion=${COUNT}
