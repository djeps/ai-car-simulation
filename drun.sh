#!/bin/bash

xhost +local:docker

docker run -it --rm \
    --user neat \
    --env DISPLAY=$DISPLAY \
    --volume /tmp/.X11-unix:/tmp/.X11-unix \
    --env XDG_RUNTIME_DIR=/tmp/runtime-root \
    ai-car-simulator:ubuntu.22.04
