FROM python:3.5
MAINTAINER Emanuele Mazzotta hello@mazzotta.me

WORKDIR /usr/src/app

COPY src/ .
COPY setup/requirements.txt .

RUN pip install -r /usr/src/app/requirements.txt

ENV PYTHONPATH /usr/src/app:$PYTHONPATH