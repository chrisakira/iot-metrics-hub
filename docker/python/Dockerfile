FROM python:3.9-slim-buster
MAINTAINER Christopher Akira França Maekawa <christopher.maekawa@gmail.com>

ARG FLASK_PORT=5000
ARG ENVIRONMENT_NAME=development 
ENV FLASK_ENV=$ENVIRONMENT_NAME \
    FLASK_APP=app.py

EXPOSE ${FLASK_PORT}

WORKDIR /app

ENV CMAKE_VERSION=3.15.0

# Install necessary packages to download and install CMake
RUN apt-get update && apt-get install -y wget gcc cmake libssl-dev build-essential 
 
# Install required packages
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        python3 \
        python3-pip \
        sqlite \
        socat \
        build-essential \
        python3-dev \
        libffi-dev \
        libldap2-dev \
        libcurl4-openssl-dev \
        libgpgme-dev \
        libssl-dev \
        bash \
        curl \
        zip \
        pkg-config \
        libmariadb-dev \ 
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip
RUN pip3 install --upgrade pip
RUN pip install --upgrade pip wheel

COPY requirements.txt ./
RUN pip3 install --no-cache-dir -r requirements.txt 

# Flask compatibility with Python 3.8
RUN pip3 uninstall dataclasses -y
RUN rm -Rf ./vendor/dataclasses-0.8.dist-info/ ./vendor/dataclasses.py

# Copy project files
COPY . .

# Entrypoint permission
RUN ["chmod", "+x", "./docker/python/entrypoint.sh"]
# Entrypoint
ENTRYPOINT ["sh", "./docker/python/entrypoint.sh"]

CMD [ "flask", "run", "--host", "0.0.0.0" ]
