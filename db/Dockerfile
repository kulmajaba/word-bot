# Image setup
FROM postgres:12

COPY ./db/visitorbot.sql /docker-entrypoint-initdb.d

WORKDIR /src

COPY .env /src