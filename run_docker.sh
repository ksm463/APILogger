#!/bin/bash

port_num="1"
CONTAINER_NAME="ksm_mockapi"
IMAGE_NAME="mockapi"
TAG="0.1"

fastapi_path=$(pwd)


docker run \
    -it \
    -p ${port_num}8000:8000 \
    --name ${CONTAINER_NAME} \
    --privileged \
    -v /tmp/.X11-unix:/tmp/.X11-unix \
    -v ${fastapi_path}:/mockapi \
    -e DISPLAY=$DISPLAY \
    --shm-size 20g \
    --restart=always \
    -w /mockapi \
    ${IMAGE_NAME}:${TAG}
