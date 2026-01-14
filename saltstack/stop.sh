#!/bin/bash
docker compose down
docker compose rm salt-master -f
docker compose rm salt-minion -f
