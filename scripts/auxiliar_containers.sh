#!/bin/bash
docker compose -f scripts/Redis/docker-compose.yml up -d
docker compose -f scripts/PostgreSQL/docker-compose.yml up -d
docker compose -f scripts/MariaDB/docker-compose.yml up -d
docker compose -f scripts/Grafana/docker-compose.yml up -d
docker compose -f scripts/InfluxDB/docker-compose.yml up -d
docker compose -f scripts/PG4Admin/docker-compose.yml up -d
docker compose -f scripts/Portainer/docker-compose.yml up -d
