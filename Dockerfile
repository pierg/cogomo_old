FROM ubuntu:19.04

# Install keyboard-configuration separately to avoid travis hanging waiting for keyboard selection
RUN \
    apt -y update && \
    apt install -y keyboard-configuration

# Install general things
RUN \
    apt install -y \
        git \
        unzip \
        nano

# Install strix dependencies
RUN \
    apt install -y \
        cmake \
        make\
        libboost-dev \
        libboost-program-options-dev \
        libboost-filesystem-dev \
        libboost-iostreams-dev \
        zlib1g-dev \
        openjdk-12-jdk

# Install CoGoMo dependencies
RUN \
    apt install -y \
        python3-pip \
        python3-dev


RUN \
    apt clean && \
    rm -rf /var/lib/apt/lists/*



WORKDIR /home

# Cloning Strix
RUN git clone https://gitlab.lrz.de/i7/strix.git

WORKDIR /home/strix

RUN \
    git submodule init && \
    git submodule update

RUN make

RUN cp ./bin/strix /usr/local/bin

WORKDIR /home

RUN git clone -b ltldev --single-branch https://github.com/pierg/cogomo.git

RUN python3 -m pip install --user --upgrade pip==9.0.3

WORKDIR /home/cogomo

ENV PYTHONPATH "${PYTHONPATH}:/home/cogomo/src"

ENTRYPOINT ["./entrypoint.sh"]