#!/bin/bash
echo "** make sure that docker running on this machine **"

echo "stopping existing containers..."
docker stop cogomo_clustering || true && docker rm cogomo_clustering || true

echo "pulling latest docker image..."
docker pull pmallozzi/cogomo:latest

if [ $# -eq 0 ]
  then
    echo "no custom input file provided, launching the default configuration"

    echo "creating new docker container..."
    docker run -t -d  --name cogomo_clustering -v "$(pwd)/default/results":/home/cogomo/output/results pmallozzi/cogomo:latest -e

    echo "results and logs will be saved in $(pwd)/default/logs.txt"
    docker logs -f cogomo_clustering >& "$(pwd)/default/logs.txt" &

    echo "launching..."
    docker exec -dit cogomo_clustering bash -c "python3 run_clustering.py"
    echo "process started..."

  else
    echo "custom input file provided, launching with: $1/input_clustering.py"

    echo "creating new docker container..."
    docker run -dit --name cogomo_clustering -v "$(pwd)/$1/results":/home/cogomo/output/results pmallozzi/cogomo:latest

    echo "results and logs will be saved in $(pwd)/$1/logs.txt"
    docker logs -f cogomo_clustering >& "$(pwd)/$1/logs.txt"

    echo "copying input file $(pwd)/$1/logs.txt"
    docker cp "$(pwd)/$1/input_clustering.py" cogomo_clustering:/home/cogomo

    echo "launching..."
    docker exec -d cogomo_clustering bash -c "python3 run_clustering.py"
    echo "process started..."

fi



