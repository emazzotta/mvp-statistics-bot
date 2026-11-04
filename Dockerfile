FROM python:3.15.2-alpine3.24

LABEL maintainer="hello@mazzotta.me"

ENV PYTHONPATH /app:$PYTHONPATH

RUN mkdir /app
WORKDIR /app

COPY requirements.txt /app
COPY src /app/src

RUN pip install -r requirements.txt

CMD ["python", "src/bot.py"]
