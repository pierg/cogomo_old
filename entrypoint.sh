#!/usr/bin/env bash

echo "...updating repository - git pull..."
git pull

echo "...evaluation launch_script..."

if [ $# -eq 0 ]
  then
    source run.sh
else
    source run.sh "$@"
fi