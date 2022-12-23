#!/usr/bin/env bash

NAME="$1"

if [[ ! -z $NAME ]]; then
    docker build --no-cache --build-arg BUILD_DATE=`date -u +%Y-%m-%dT%H:%M:%SZ` -t $NAME .
else
  echo "not found name"
  echo "example: $0 'image:tag'"
fi