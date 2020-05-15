#!/bin/bash

docker stop cogomo_clustering || true && docker rm cogomo_clustering || true

# Create docker container
docker create --name cogomo_clustering -v "$(pwd)/$1":/home/cogomo/output pmallozzi/cogomo:latest -c

# Copy the input file
docker cp "$(pwd)/$1/clustering_mission_default.py" cogomo_clustering:/home/cogomo/

# Start the container in clustering mode
docker start cogomo_clustering
