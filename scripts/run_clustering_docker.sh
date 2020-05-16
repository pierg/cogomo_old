#!/bin/bash

echo "stopping existing containers..."
docker stop cogomo_clustering || true && docker rm cogomo_clustering || true

echo "pulling latest docker image..."
docker pull pmallozzi/cogomo:latest

echo "creating new docker container..."
docker run -d --name cogomo_clustering -v "$(pwd)/$1/results":/home/cogomo/output/results pmallozzi/cogomo:latest -e

echo "logs will be saved in logs.txt"
docker logs -f cogomo_clustering >& "$(pwd)/$1/logs.txt"


if [ $# -eq 0 ]
  then
    echo "No custom input file provided"
    echo "Launching the default configuration"
    echo "logs will be saved in $(pwd)/logs.txt"
    docker logs -f cogomo_clustering >& "$(pwd)/logs.txt"
fi

echo "copying the custom"
docker cp "$(pwd)/$1/input_clustering.py" cogomo_clustering:/home/

# Start the container in clustering mode
docker start -i cogomo_clustering



