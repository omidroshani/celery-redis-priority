FROM python:3.8

ENV PYTHONUNBUFFERED 1

RUN mkdir /opt/sample-app

WORKDIR /opt/sample-app


ADD core/requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

ADD core/ .