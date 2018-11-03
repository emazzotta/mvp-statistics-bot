FROM python:3.7-alpine3.8

MAINTAINER Emanuele Mazzotta hello@mazzotta.me

ENV PYTHONPATH /app:$PYTHONPATH

RUN mkdir /app
WORKDIR /app

COPY requirements.txt /app
COPY src /app/src

RUN pip install -r requirements.txt

CMD ["python", "src/bot.py"]
