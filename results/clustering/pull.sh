#!/bin/bash
git reset --hard HEAD
git clean -f -x -d -n
git pull
