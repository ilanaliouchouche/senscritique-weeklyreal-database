FROM ubuntu:latest

RUN apt-get update && apt-get install -y \
    wget \
    gnupg2 \
    unzip \
    build-essential \
    zlib1g-dev \
    libncurses5-dev \
    libgdbm-dev \
    libnss3-dev \
    libssl-dev \
    libreadline-dev \
    libffi-dev \
    libsqlite3-dev \
    libbz2-dev

RUN wget https://www.python.org/ftp/python/3.11.5/Python-3.11.5.tgz \
    && tar -xf Python-3.11.5.tgz \
    && cd Python-3.11.5 \
    && ./configure --enable-optimizations \
    && make -j 4 \
    && make altinstall

RUN ln -s /usr/local/bin/python3.11 /usr/local/bin/python \
    && ln -s /usr/local/bin/pip3.11 /usr/local/bin/pip

COPY etl /bddr-sc/etl
COPY .env /bddr-sc/.env
COPY main.py /bddr-sc/main.py
COPY setup_vcb.py /bddr-sc/setup_vcb.py
COPY requirements.txt /tmp/requirements.txt

RUN pip install -r /tmp/requirements.txt

ENV PYTHONPATH "${PYTHONPATH}:/bddr-sc"

WORKDIR /bddr-sc


CMD ["python", "main.py"]




