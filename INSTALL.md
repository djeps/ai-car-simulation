[Home](README.md)

# Setting up the environment and running the simulation

In principle, you could just clone the repo and launch the game with:

```shell
python3 main.py
```

The game accepts command line arguments (some of the more important parameters which affect
the simulation), but while it also assigns some default values, it also gives the user the
opportunity to change them from the game loop itself.

Running it this way, your Python interpreter will more than likely throw in a few errors
about missing modules - unless you happen to have the exact same setup as mine.

> NOTE: My `Python3` interpreter version is `3.10.12`

In such a case, you could continue by installing them with `pip` one by one, but the best
approach would be to **create a virtual Python environment** and:

- manually install all the missing modules yourself or
- use the provided `requirements.txt` file

## Installing using the `requirements.txt` file

First, create a virtual Python environment:

```shell
cd ai-car-cimulation
mkdir venv
python3 -m venv venv/ai-car-simulation
```

Then activate the environment and install the dependencies:

```shell
source venv/bai-car-simulation/bin/activate
pip3 install -r requirements.txt
```

The `graphviz` system packgae is also required. Make sure you install it as well with:

```shell
sudo apt install graphviz
```

... and try re-running the game:

```shell
python3 main.py
```

## Starting up the game inside a Docker container

All of the previous instructions were with an assumption your host machine runs a debian based
OS, but you can adapt it to any Linux distribution.

By far the most straightforward way (aside the fact you need to have Docker already installed,
which I will not cover here as it's out-of-scope) is to launch the game inside a Docker container.

To do so, you ordinarilly would have to either:

- Pull a pre-built Docker image or
- Build the Docker image yourself using the provided `Docker` file

### Building the Docker image

To build the image from the provided `Docker` file:

```shell
docker build \
    --build-arg USER_UID=$(id -u) \
    --build-arg USER_GID=$(id -g) \
    -t ai-car-simulator:ubuntu.22.04 .
```

... or use the utility wrapper script:

```shell
./dbuild.sh
```

Then we need to enable X11 forwarding by:

```shell
xhost +local:docker
```

... and then we can simply run the container by:

```shell
docker run -it --rm \
    --user neat \
    --env DISPLAY=$DISPLAY \
    --volume /tmp/.X11-unix:/tmp/.X11-unix \
    --env XDG_RUNTIME_DIR=/tmp/runtime-root \
    ai-car-simulator:ubuntu.22.04
```

... or use the utility wrapper script:

```shell
./drun.sh
```

The application should start automatically and the container shut down once you exit the application.

> NOTE: I haven't tested this on a Windows host OS running Docker... 

[Home](README.md)
