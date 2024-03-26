FROM python:3.12-alpine

ENV PYTHONUNBUFFERED 1

COPY ./requirements.txt /requirements.txt

RUN apk add --update --no-cache --virtual .tmp-build-deps \
    gcc libc-dev linux-headers postgresql-dev musl-dev zlib zlib-dev

RUN pip install -r requirements.txt

RUN apk del .tmp-build-deps


RUN adduser \
        --disabled-password \
        --no-create-home \
        django-user

USER django-user

WORKDIR /app

COPY . .
