FROM ubuntu:19.10

ENV DEBIAN_FRONTEND=noninteractive

# Istall binary files of strix and nuXmv
COPY bin/linux/strix /usr/local/bin
COPY bin/linux/owl.jar /usr/local/bin
RUN chmod +x /usr/local/bin/strix

COPY bin/linux/nuXmv /usr/local/bin
RUN chmod +x /usr/local/bin/nuXmv

RUN sed -i -e 's|disco|eoan|g' /etc/apt/sources.list

# Install keyboard-configuration separately to avoid travis hanging waiting for keyboard selection
RUN \
    apt -y update && \
    apt install -y --allow-unauthenticated keyboard-configuration

# Install general things
RUN \
    apt install -y --allow-unauthenticated \
        git \
        unzip \
        nano \
        wget \
        gnupg2 \
        tzdata

RUN apt update && \
    apt install -y --allow-unauthenticated software-properties-common && \
    rm -rf /var/lib/apt/lists/*

RUN apt --allow-releaseinfo-change update
RUN apt update
RUN \
    apt install -y --allow-unauthenticated \
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
    apt install -y --allow-unauthenticated \
        python3-pip \
        python3-dev


# Needed for spot
RUN wget -q -O - https://www.lrde.epita.fr/repo/debian.gpg | apt-key add -
RUN echo 'deb http://www.lrde.epita.fr/repo/debian/ stable/' >> /etc/apt/sources.list

RUN apt -y update && DEBIAN_FRONTEND=noninteractive && \
    apt install -y --allow-unauthenticated \
    spot \
    libspot-dev \
    spot-doc



RUN \
    apt clean && \
    rm -rf /var/lib/apt/lists/*


WORKDIR /home

RUN git clone -b master --single-branch https://github.com/pierg/cogomo.git

RUN python3 -m pip install --user --upgrade pip

WORKDIR /home/cogomo


RUN pip3 install -r requirements.txt

ENV PYTHONPATH "${PYTHONPATH}:/home/cogomo:/home/cogomo/src:/home/cogomo/src/z3"

ENTRYPOINT ["./entrypoint.sh"]
