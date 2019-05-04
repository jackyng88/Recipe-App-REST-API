FROM python:3.7-alpine
MAINTAINER Jacky App

ENV PYTHONUNBUFFERED 1

COPY ./requirements.txt /requirements.txt
RUN apk add --update --no-cache postgresql-client jpeg-dev
RUN apk add --update --no-cache --virtual .tmp-build-deps \
      gcc libc-dev linux-headers postgresql-dev musl-dev zlib zlib-dev
RUN pip install -r /requirements.txt
RUN apk del .tmp-build-deps

RUN mkdir /app
WORKDIR /app
COPY ./app /app

RUN mkdir -p /vol/web/media
RUN mkdir -p /vol/web/static
# -p gives the instruction to create /vol/ for instance if it doesn't exist.
RUN adduser -D user
RUN chown -R user:user /vol
# chown sets ownership of all of /vol/ to the user, and -R means recursive
# thus the subdirectories and their subdirectories are affected as well.
RUN chmod -R 755 /vol/web
# this means the user can do everything with the directory
USER user
