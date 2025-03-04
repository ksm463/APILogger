#!/bin/bash

IMAGE_NAME="mockapi"
TAG="0.1"

docker build --no-cache --progress=plain -t ${IMAGE_NAME}:${TAG} . > build.log
