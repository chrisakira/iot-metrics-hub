#!/bin/bash

if [[ $(sudo docker info --format '{{.Swarm.LocalNodeState}}') == "active" ]]; then
  echo "Already part of a Swarm"
  echo "Run 'docker swarm leave --force' to leave the current Swarm"
  exit 0
fi

# Initialize Docker Swarm
sudo docker swarm init

# Get the Swarm manager token
manager_token=$(sudo docker swarm join-token manager -q)

# Get the Swarm worker token
worker_token=$(sudo docker swarm join-token worker -q)


# Display the tokens to join the Swarm
echo "Swarm manager token: $manager_token"
echo "Swarm worker token: $worker_token"

# Write the tokens to a JSON file
echo "{\"manager_token\": \"$manager_token\", \"worker_token\": \"$worker_token\"}" > tokens.json
