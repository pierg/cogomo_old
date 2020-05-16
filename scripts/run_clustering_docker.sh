#!/bin/bash
echo "** make sure that docker running on this machine **"

echo "stopping existing containers..."
docker stop cogomo_clustering || true && docker rm cogomo_clustering || true

echo "pulling latest docker image..."
docker pull pmallozzi/cogomo:latest

if [ $# -eq 0 ]
  then
    echo "  no custom input file provided, launching the default configuration"

    echo "  creating new docker container..."
    docker create -i -t  --name cogomo_clustering -v "$(pwd)/default/results":/home/cogomo/output/results pmallozzi/cogomo:latest -c

    echo "  results and logs will be saved in $(pwd)/default/logs.txt"
    docker logs -f cogomo_clustering >& "$(pwd)/default/logs.txt" &

    echo "  starting docker..."
    docker start cogomo_clustering

  else
    echo "  custom input file provided, launching with: $1/input_clustering.py"

    echo "  creating new docker container..."
    docker create -i -t  --name cogomo_clustering -v "$(pwd)/default/results":/home/cogomo/output/results pmallozzi/cogomo:latest -c

    echo "copying input file $(pwd)/$1/logs.txt"
    docker cp "$(pwd)/$1/input_clustering.py" cogomo_clustering:/home/

    echo "  results and logs will be saved in $(pwd)/$1/logs.txt"
    docker logs -f cogomo_clustering >& "$(pwd)/$1/logs.txt" &

    echo "  starting docker..."
    docker start cogomo_clustering

fi



