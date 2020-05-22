#!/bin/bash
git fetch --prune origin
git reset --hard origin/master
git clean -f -d