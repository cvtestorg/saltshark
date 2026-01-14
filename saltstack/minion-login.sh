#!/bin/bash
INDEX=${1:-1}
docker-compose exec --index=${INDEX} salt-minion bash
