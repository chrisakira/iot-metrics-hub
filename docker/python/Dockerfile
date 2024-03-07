FROM debian:bullseye-slim
MAINTAINER Christopher Akira França Maekawa <christopher.maekawa@gmail.com>

ARG FLASK_PORT=5000
ARG ENVIRONMENT_NAME=development 
ENV FLASK_ENV=$ENVIRONMENT_NAME \
    FLASK_APP=app.py

EXPOSE ${FLASK_PORT}

WORKDIR /app

# update and upgrade
RUN apt-get update -y && apt-get upgrade -y

# Install required packages
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        python3 \
        python3-pip \
        gcc g++ \
        wget \
        libssl-dev \
        build-essential \
        libmariadb-dev \
        libmariadb-dev-compat \
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
        software-properties-common \
        libpq-dev \
        libatlas-base-dev \
        gfortran\
        libxml2-dev \
        libxslt-dev \
        python-dev \ 
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip
RUN pip3 install --upgrade pip
RUN pip3 install --upgrade pip wheel

ENV TZ=America/Sao_Paulo

RUN apt-get update && DEBIAN_FRONTEND=noninteractive apt-get install -y tzdata && \
    ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

RUN wget --no-check-certificate -O - https://apt.kitware.com/keys/kitware-archive-latest.asc | gpg --dearmor -o /usr/share/keyrings/kitware-archive-keyring.gpg && \
    echo "deb [signed-by=/usr/share/keyrings/kitware-archive-keyring.gpg] https://apt.kitware.com/ubuntu/ bionic main" > /etc/apt/sources.list.d/kitware.list

RUN apt-get install -y --no-install-recommends cmake && rm -rf /var/lib/apt/lists/*

COPY requirements.txt ./
RUN pip3 install --no-cache-dir -r requirements.txt 

RUN pip3 uninstall dataclasses -y
RUN rm -Rf ./vendor/dataclasses-0.8.dist-info/ ./vendor/dataclasses.py

# Copy project files
COPY . .

# Entrypoint permission
RUN ["chmod", "+x", "./docker/python/entrypoint.sh"]
# Entrypoint
ENTRYPOINT ["sh", "./docker/python/entrypoint.sh"]

CMD [ "flask", "run", "--host", "0.0.0.0" ]
