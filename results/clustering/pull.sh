#!/bin/bash
sudo git fetch --prune origin
sudo git reset --hard origin/master
sudo git clean -f -d