#!/bin/bash
sudo chown -R $(id -u):$(id -g) "$(git rev-parse --show-toplevel)/.git"
git fetch --prune origin
git reset --hard origin/master
git pull