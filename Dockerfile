# Specify the base image
FROM ubuntu:22.04

# Avoid prompts from apt
ENV DEBIAN_FRONTEND=noninteractive

# Create a non-root user
ENV USER_NAME=neat
ARG USER_UID=1000
ARG USER_GID=$USER_UID

# Setup the non-root user
RUN groupadd --gid $USER_GID $USER_NAME \
  && useradd -s /bin/bash --uid $USER_UID --gid $USER_GID -m $USER_NAME \
  && mkdir /home/$USER_NAME/.config \
  && chown $USER_UID:$USER_GID /home/$USER_NAME/.config

# Update and install necessary packages
RUN apt-get update && apt-get install -y \
      nano \
      python3 \
      python3-pip \
      graphviz \
      libsdl2-2.0-0 \
      libsdl2-mixer-2.0-0 \
      libsdl2-image-2.0-0 \
    && apt-get clean all \
    && rm -rf /var/lib/apt/lists/*

# Set the working directory
WORKDIR /home/${USER_NAME}/ai-car-simulation

# Copy the application files
COPY ./open_sans/ /home/${USER_NAME}/ai-car-simulation/open_sans/
COPY ./images/ /home/${USER_NAME}/ai-car-simulation/images/
COPY ./args.py /home/${USER_NAME}/ai-car-simulation/
COPY ./car.py /home/${USER_NAME}/ai-car-simulation/
COPY ./config.ini /home/${USER_NAME}/ai-car-simulation/
COPY ./config.txt /home/${USER_NAME}/ai-car-simulation/
COPY ./constants.py /home/${USER_NAME}/ai-car-simulation/
COPY ./game.py /home/${USER_NAME}/ai-car-simulation/
COPY ./game.py /home/${USER_NAME}/ai-car-simulation/
COPY ./main.py /home/${USER_NAME}/ai-car-simulation/
COPY ./menu.py /home/${USER_NAME}/ai-car-simulation/
COPY ./neural_network.py /home/${USER_NAME}/ai-car-simulation/
COPY ./obstacle.py /home/${USER_NAME}/ai-car-simulation/
COPY ./visualize.py /home/${USER_NAME}/ai-car-simulation/
COPY ./requirements.txt /home/${USER_NAME}/ai-car-simulation/

# Change ownership of the working directory
RUN chown -R ${USER_NAME}:${USER_NAME} /home/${USER_NAME}/ai-car-simulation

# Install any additional Python dependencies
RUN pip3 install --no-cache-dir -r requirements.txt

# Install the 'Open Sans' font
RUN mkdir -p /usr/share/fonts/truetype/opensans
RUN find /home/${USER_NAME}/ai-car-simulation/open_sans -name '*.ttf' -exec cp {} /usr/share/fonts/truetype/opensans \;
RUN fc-cache -f -v

# Swtich to the 'neat' non-root user
USER ${USER_NAME}

# Start the application as the 'neat' user
#CMD ["python3", "/home/${USER_NAME}/ai-car-simulation/main.py"]
CMD ["sh", "-c", "echo /home/${USER_NAME}/ai-car-simulation/main.py | xargs python3"]
