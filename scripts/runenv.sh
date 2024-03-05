#!/bin/bash
if test -f ./scripts/preenv.sh; then
    source ./scripts/preenv.sh;
else
    echo './scripts/preenv.sh not found'
fi
export TEST_ENV=0
export LOCALHOST=$(ifconfig docker0| grep -Eo 'inet (addr:)?([0-9]*\.){3}[0-9]*' | grep -Eo '([0-9]*\.){3}[0-9]*' | grep -v '127.0.0.1')
# sudo docker buildx build --platform linux/amd64,linux/arm64,linux/arm/v7 -t chrisakira/akirapi:0.0.2 -f ./docker/python/Dockerfile . --push


sudo docker compose up $1 $2 $