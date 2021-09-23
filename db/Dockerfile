# Image setup
FROM postgres:12

COPY ./db/wordbot.sql /docker-entrypoint-initdb.d
COPY ./db/init_words.sql /docker-entrypoint-initdb.d

WORKDIR /src

COPY .env /src