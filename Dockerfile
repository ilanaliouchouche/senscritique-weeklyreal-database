# Dockerfile for the BDDR-SC project
FROM python:3.11.5

RUN apt-get update && apt-get install wget unzip && \
    wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb && \
    apt-get install -y ./google-chrome-stable_current_amd64.deb && \
    rm google-chrome-stable_current_amd64.deb && \
    apt-get clean 

COPY etl /bddr-sc/etl
COPY .env /bddr-sc/.env
COPY main.py /bddr-sc/main.py
COPY setup_vcb.py /bddr-sc/setup_vcb.py
COPY requirements.txt /tmp/requirements.txt

RUN pip install --trusted-host pypi.pyton.org -r /tmp/requirements.txt

ENV PYTHONPATH "${PYTHONPATH}:/bddr-sc"

WORKDIR /bddr-sc

CMD tail -f /dev/null






