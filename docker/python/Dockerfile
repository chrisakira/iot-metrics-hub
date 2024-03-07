FROM debian:bullseye-slim
MAINTAINER Christopher Akira França Maekawa <christopher.maekawa@gmail.com>

ARG FLASK_PORT=5000
ARG ENVIRONMENT_NAME=development 
ENV FLASK_ENV=$ENVIRONMENT_NAME \
    FLASK_APP=app.py

EXPOSE ${FLASK_PORT}

WORKDIR /app

# Install necessary packages
RUN apt-get update -y && apt-get upgrade -y

RUN apt install -y python3-pip

RUN apt-get install -y gcc g++
 
RUN apt-get install -y wget libssl-dev build-essential

RUN apt-get install -y libmariadb-dev libmariadb-dev-compat 
 
# Install required packages
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        python3 \
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
        libssl1.1 \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip
RUN pip3 install --upgrade pip
RUN pip3 install --upgrade pip wheel

COPY requirements_confirmed.txt ./
RUN pip3 install --no-cache-dir -r requirements_confirmed.txt 

ENV TZ=America/Sao_Paulo

RUN apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y tzdata && \
    ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

RUN apt-get update && apt-get install -y software-properties-common libpq-dev && \
    wget --no-check-certificate -O - https://apt.kitware.com/keys/kitware-archive-latest.asc | gpg --dearmor -o /usr/share/keyrings/kitware-archive-keyring.gpg && \
    echo "deb [signed-by=/usr/share/keyrings/kitware-archive-keyring.gpg] https://apt.kitware.com/ubuntu/ bionic main" > /etc/apt/sources.list.d/kitware.list

RUN apt-get update -y && apt-get upgrade -y

RUN apt-get install -y cmake

RUN apt-get update && apt-get install -y \
    libatlas-base-dev gfortran \
    && pip install numpy

RUN apt-get update && apt-get install -y \
    libxml2-dev \
    libxslt-dev \
    python-dev
COPY requirements.txt ./
RUN pip3 install --no-cache-dir -r requirements.txt 

# Flask compatibility with Python 3.8
RUN pip3 install --no-cache-dir flask-cors asammdf

RUN pip3 uninstall dataclasses -y
RUN rm -Rf ./vendor/dataclasses-0.8.dist-info/ ./vendor/dataclasses.py

# Copy project files
COPY . .

# Entrypoint permission
RUN ["chmod", "+x", "./docker/python/entrypoint.sh"]
# Entrypoint
ENTRYPOINT ["sh", "./docker/python/entrypoint.sh"]

CMD [ "flask", "run", "--host", "0.0.0.0" ]
