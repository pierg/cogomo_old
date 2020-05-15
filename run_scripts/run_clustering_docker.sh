#!/bin/bash

docker stop cogomo_clustering || true && docker rm cogomo_clustering || true

docker pull pmallozzi/cogomo:latest

# Create docker container
docker create -it --name cogomo_clustering -v "$(pwd)/$1/results":/home/cogomo/output/results pmallozzi/cogomo:latest -c

# Copy the input file
docker cp "$(pwd)/$1/input_clustering_custom.py" cogomo_clustering:/home/cogomo/

# Start the container in clustering mode
docker start -i cogomo_clustering
