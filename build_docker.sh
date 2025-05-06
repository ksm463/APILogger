#!/bin/bash

IMAGE_NAME="apilogger"
TAG="0.1"

docker build --no-cache --progress=plain -t ${IMAGE_NAME}:${TAG} . 
