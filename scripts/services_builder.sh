#!/bin/bash
sudo  docker network create -d overlay --attachable IoT_Metrics_Network 
sudo docker compose -f ./scripts/Portainer/docker-compose.yml up -d
sudo docker stack deploy -c ./scripts/Traeffik/docker-compose.yml traefik
sudo docker stack deploy -c ./scripts/MariaDB/docker-compose.yml traefik

